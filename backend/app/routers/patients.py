from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, cast
from math import ceil

from app import crud, models, schemas
from app.database import get_db, UserRole
from app.dependencies import (
    get_current_active_user,
    get_current_active_admin,
    get_current_clinic_staff_or_admin,
    get_current_patient_or_doctor_or_admin
)

router = APIRouter(
    tags=["Patients"] # Removed prefix="/patients"
)

@router.post("/", response_model=schemas.PatientSchema, status_code=status.HTTP_201_CREATED)
def create_new_patient(
    patient_in: schemas.PatientCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_clinic_staff_or_admin) # Use imported dependency
):
    user_for_patient = crud.get_user(db, user_id=patient_in.user_id)
    if not user_for_patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {patient_in.user_id} not found.")
    if user_for_patient.role.value != UserRole.PATIENT.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User with id {patient_in.user_id} is not a Patient.")

    existing_patient = crud.get_patient_by_user_id(db, user_id=patient_in.user_id) # This function needs to be added to crud.py
    if existing_patient:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Patient profile already exists for user id {patient_in.user_id}")
    
    creator_id = cast(int, current_user.id)
    return crud.create_patient(db=db, patient_in=patient_in, creator_id=creator_id)

@router.get("/", response_model=List[schemas.PatientSchema])
def list_all_patients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    current_user_role = current_user.role.value
    current_user_id = cast(int, current_user.user_id)

    if current_user_role == UserRole.ADMIN.value or current_user_role == UserRole.CLINIC_STAFF.value:
        patients = crud.get_patients(db, skip=skip, limit=limit)
    elif current_user_role == UserRole.DOCTOR.value:
        patients = crud.get_patients_by_doctor(db, doctor_id=current_user_id, skip=skip, limit=limit)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions to view all patients")
    return patients


@router.get("/{patient_id}", response_model=schemas.PatientSchema)
def get_patient_details(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_patient_or_doctor_or_admin) # Use imported dependency
):
    db_patient = crud.get_patient(db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    current_user_role_val = current_user.role.value
    current_user_id_val = cast(int, current_user.id)
    
    patient_user_id_val = cast(int, db_patient.user_id)
    assigned_doctor_id_val = cast(int, db_patient.assigned_doctor_id) if db_patient.assigned_doctor_id is not None else None

    if (current_user_role_val == UserRole.ADMIN.value or
            current_user_role_val == UserRole.CLINIC_STAFF.value):
        return db_patient
    if current_user_role_val == UserRole.DOCTOR.value and assigned_doctor_id_val == current_user_id_val:
        return db_patient
    if current_user_role_val == UserRole.PATIENT.value and patient_user_id_val == current_user_id_val:
        return db_patient
    
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions to view this patient's details")


@router.put("/{patient_id}", response_model=schemas.PatientSchema)
def update_patient_details(
    patient_id: int,
    patient_update_data: schemas.PatientUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    db_patient = crud.get_patient(db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    current_user_role_val = current_user.role.value
    current_user_id_val = cast(int, current_user.id)
    
    # Get current values from db_patient safely for comparison
    assigned_doctor_id_val = cast(int, db_patient.assigned_doctor_id) if db_patient.assigned_doctor_id is not None else None
    # Ensure emr_summary from db is treated as a string for comparison, handling None
    db_patient_emr_str_val = str(db_patient.emr_summary) if db_patient.emr_summary is not None else None

    can_update = False
    if current_user_role_val == UserRole.ADMIN.value:
        can_update = True
    elif current_user_role_val == UserRole.CLINIC_STAFF.value:
        if (patient_update_data.assigned_doctor_id is not None and
                patient_update_data.assigned_doctor_id != assigned_doctor_id_val): # Used assigned_doctor_id_val
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Clinic staff cannot change the assigned doctor.")
        
        # Original logic: error if clinic staff provides an EMR summary AND it's different from current.
        if (patient_update_data.emr_summary is not None and
                db_patient_emr_str_val != patient_update_data.emr_summary): # Used db_patient_emr_str_val
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Clinic staff cannot update EMR summary via this general update endpoint.")
        can_update = True
    elif current_user_role_val == UserRole.DOCTOR.value and assigned_doctor_id_val == current_user_id_val:
        if (patient_update_data.assigned_doctor_id is not None and
                patient_update_data.assigned_doctor_id != assigned_doctor_id_val): # Used assigned_doctor_id_val
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Doctors cannot change the assigned doctor for a patient via this endpoint.")
        can_update = True
    
    if not can_update:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions to update this patient")
        
    return crud.update_patient(db=db, patient_id=patient_id, patient_update=patient_update_data)


@router.delete("/{patient_id}", response_model=schemas.PatientSchema)
def remove_patient_record(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_admin)
):
    db_patient = crud.get_patient(db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return crud.delete_patient(db=db, patient_id=patient_id)


@router.post("/{patient_id}/assign-doctor/{doctor_id}", response_model=schemas.PatientSchema)
def assign_doctor_to_patient_record(
    patient_id: int,
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_clinic_staff_or_admin) # Use imported dependency
):
    db_patient = crud.get_patient(db, patient_id=patient_id)
    if not db_patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    
    db_doctor = crud.get_user(db, user_id=doctor_id)
    if not db_doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {doctor_id} not found.")
    if db_doctor.role.value != UserRole.DOCTOR.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User with id {doctor_id} is not a Doctor.")
        
    updated_patient = crud.update_patient(db=db, patient_id=patient_id, patient_update=schemas.PatientUpdate(assigned_doctor_id=doctor_id))
    if not updated_patient:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to assign doctor to patient.")
    return updated_patient

@router.put("/{patient_id}/emr", response_model=schemas.PatientSchema)
def update_patient_emr_summary_route( # Renamed to avoid conflict if any other update_patient_emr_summary exists
    patient_id: int,
    emr_update: schemas.PatientEMRUpdate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    db_patient = crud.get_patient(db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    current_user_role_val = current_user.role.value
    current_user_id_val = cast(int, current_user.id)
    # Ensure db_patient.assigned_doctor_id is accessed correctly
    assigned_doctor_id_val = cast(int, db_patient.assigned_doctor_id) if db_patient.assigned_doctor_id is not None else None


    can_update_emr = False
    if current_user_role_val == UserRole.ADMIN.value:
        can_update_emr = True
    elif current_user_role_val == UserRole.DOCTOR.value and assigned_doctor_id_val == current_user_id_val:
        can_update_emr = True
    
    if not can_update_emr:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions to update EMR for this patient")

    # The crud.update_patient_emr was fixed to: `update_patient_emr(db: Session, patient_id: int, emr_summary: str)`
    # The schema PatientEMRUpdate has `emr_summary: Optional[str]`. If it's None, we might not want to update.
    # However, the CRUD function expects a string.
    if emr_update.emr_summary is None:
        # Or raise HTTPException if emr_summary is required for this endpoint
        return db_patient # No update if summary is None

    return crud.update_patient_emr(db=db, patient_id=patient_id, emr_summary=emr_update.emr_summary)

@router.post("/search", response_model=schemas.PatientSearchResponse)
def search_patients(
    search_params: schemas.PatientSearchQuery,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Advanced patient search with multiple criteria and role-based access control.
    
    - **Doctors**: Can only search their assigned patients
    - **Patients**: Can only search their own record  
    - **Admin/Staff**: Can search all patients
    
    Supports searching by name, email, phone, ID, age ranges, and more.
    """
    current_user_role = current_user.role.value
    current_user_id = cast(int, current_user.user_id)
    
    # Get search results with total count
    patients, total_count = crud.search_patients(
        db=db,
        search_params=search_params,
        current_user_role=current_user_role,
        current_user_id=current_user_id
    )
    
    # Convert to search result format with computed fields
    patient_results = []
    for patient in patients:
        search_result = crud.get_patient_search_result(db=db, patient=patient)
        patient_results.append(search_result)
    
    # Calculate pagination info
    per_page = search_params.limit
    current_page = (search_params.skip // per_page) + 1
    total_pages = ceil(total_count / per_page) if per_page > 0 else 1
    
    return schemas.PatientSearchResponse(
        patients=patient_results,
        total_count=total_count,
        page=current_page,
        per_page=per_page,
        total_pages=total_pages
    )
