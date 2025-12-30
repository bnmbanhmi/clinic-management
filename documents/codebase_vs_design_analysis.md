# Codebase vs Design Analysis Report

This report compares the existing database schema implementation in `backend/app/models.py` with the design specifications in `documents/table_design.md`.

## Summary
The codebase implementation deviates significantly from the design document. Several tables are missing, others have different column names or types, and the relationship structure differs in some areas (notably the Shared Primary Key pattern used in User/Doctor/Patient vs separate IDs in design).

## Detailed Field Comparison

### 1. User Table
| Feature | Design (`table_design.md`) | Implementation (`models.py`) | Status |
| :--- | :--- | :--- | :--- |
| **PK** | `user_id` | `user_id` | ✅ Match |
| **Email** | `email` (UNIQUE, NOT NULL) | `email` (Nullable per default, no unique constraint defined in `Column`) | ⚠️ Mismatch |
| **Username** | *Not specified* | `username` (NOT NULL) | ⚠️ Extra field in code |
| **Name** | `full_name` | `full_name` | ✅ Match |
| **Role** | `role` | `role` (Enum) | ✅ Match |
| **Password** | `hashed_password` | `hashed_password` | ✅ Match |

### 2. Patient Table
| Feature | Design | Implementation | Status |
| :--- | :--- | :--- | :--- |
| **PK** | `patient_id` | `patient_id` (FK to `users.user_id`) | ⚠️ Logic diff (Structure: `User` -> `Patient`) |
| **Relationships** | `user_id` FK | `patient_id` is also FK to `users` | ⚠️ Implementation uses Shared PK |
| **Name** | *In User table* | `full_name` (Duplicated) | ⚠️ Redundant data |
| **Phone** | `phone` | `phone_number` | ⚠️ Naming diff |
| **Extra Fields** | - | `ethnic_group`, `health_insurance_card_no`, `identification_id`, `job`, `class_role` | ⚠️ Extra fields in code |

### 3. Doctor Table
| Feature | Design | Implementation | Status |
| :--- | :--- | :--- | :--- |
| **PK** | `doctor_id` | `doctor_id` (FK to `users.user_id`) | ⚠️ Logic diff (Shared PK) |
| **Specialization** | `specialization` | `major` | ⚠️ Naming diff |
| **Description** | `description` | *Missing* | ❌ Missing in code |
| **Name** | *In User table* | `doctor_name` (Duplicated) | ⚠️ Redundant data |

### 4. Hospital Table
| Feature | Design | Implementation | Status |
| :--- | :--- | :--- | :--- |
| **Name** | `name` | `hospital_name` | ⚠️ Naming diff |
| **Extra Fields** | - | `governed_by` | ⚠️ Extra field in code |

### 5. Appointment Table
| Feature | Design | Implementation | Status |
| :--- | :--- | :--- | :--- |
| **Date** | `appointment_date` | `appointment_day` | ⚠️ Naming diff |
| **Service** | `service` | *Missing* | ❌ Missing in code |
| **Status** | `status` | *Missing* | ❌ Missing in code |
| **Extra Fields** | - | `reason`, `re_examination_date`, `re_examination_time`, `issue` | ⚠️ Extra fields in code |

### 6. MedicalReport (vs MedicalRecord)
*Note: Code uses `MedicalReport` model.*

| Feature | Design | Implementation | Status |
| :--- | :--- | :--- | :--- |
| **ID** | `report_id` | `record_id` | ⚠️ Naming diff |
| **Appointment** | `appointment_id` FK | *Missing* | ❌ Missing link to appointment |
| **Created At** | `created_at` | *Missing* (Has `in_day`/`out_day`) | ⚠️ Logic diff |
| **Content** | `notes`, `diagnosis` | Highly detailed (vitals, history, diagnosis `in`/`out`, etc.) | ⚠️ Code is richer |
| **Prescription** | *Separate Table* | `prescription` (Text column) | ⚠️ Denormalized in code |

### 7. Missing Tables in Code
The following tables exist in the design but are **completely missing** from `models.py`:
- `Staff`
- `Prescription` (Merged into MedicalReport as text)
- `OTCMedicationRecord`

### 8. ChatMessage
- **Design**: `message_id`, `user_id`, `content`, `role`, `timestamp`.
- **Code**: `chat_id`, `user_id`, `chat_message`, `time_stamp`.
- **Mismatch**: `role` missing in code layout (though might be joined from user). `content` renamed to `chat_message`.

## Recommendations
1.  **Standardize Naming**: Align field names (e.g., `phone` vs `phone_number`, `major` vs `specialization`).
2.  **Schema Alignment**: Decide whether to adopt the detailed `MedicalReport` schema from code into design, or simplify code. The code seems to support a more complex hospital workflow (in/out patient) than the simple design.
3.  **Missing Tables**: Implement `Staff` and `OTCMedicationRecord` if features are needed.
4.  **Normalization**: Consider moving `prescription` out of `MedicalReport` if structured data is required (as per design).
5.  **Constraints**: Add proper constraints (UNIQUE, NOT NULL) to `models.py` to match design guarantees.

## Frontend Analysis

### 1. Services
*   **Design**: Specifies `AuthService`, `UserService`, `AppointmentService`, `MedicalRecordService`, `ChatService`.
*   **Implementation**: The `frontend/src/services` directory is **missing**. API logic appears to be scattered or integrated directly into components (e.g., `fetch` calls in `App.tsx`). This violates the separation of concerns design pattern.

### 2. Types
*   **Design**: Specifies `UserType`, `PatientType`, `DoctorType`, `AppointmentType`, `MedicalRecordType`, `ChatMessageType`.
*   **Implementation**: Only `UserType.tsx` exists in `frontend/src/types` and it only contains a `UserRole` enum. Other types are likely missing or defined implicitly/inline, leading to potential type safety issues.

### 3. Components
*   **Design**: Detailed component list including `Navbar`, `Sidebar`, `AppointmentCard/List/Form`, `ChatBox`, etc.
*   **Implementation**:
    *   `Sidebar` exists in `components/layout`.
    *   `Navbar` missing (possibly part of `BaseDashboard`).
    *   Appointment components (`BookAppointment`, `ViewAppointment`, `DoctorSchedule`) exist but don't strictly match the "Card/List/Form" breakdown.
    *   `ChatbotWidget` exists (for Chatbot), but generic `ChatBox` for doctor-patient chat is not clearly identified.
    *   **Structure**: Components are mixed between `src/components` and `src/pages` without clear distinction (e.g., `LoginPage` in `components` vs `Profile` in `pages`).

### 4. General
*   **Design Compliance**: Low. The frontend implementation lacks the structured approach (Services, Types, clear Component hierarchy) outlined in the design document.
