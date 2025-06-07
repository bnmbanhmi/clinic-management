import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './PatientSearch.css';

const BACKEND_URL = (process.env.REACT_APP_BACKEND_URL || '').replace(/\/+$/, '');

// Types for patient search - matching backend schema exactly
interface PatientSearchQuery {
  query?: string;
  patient_id?: number;
  full_name?: string;
  phone_number?: string;
  email?: string;
  identification_id?: string;
  health_insurance_card_no?: string;
  assigned_doctor_id?: number;
  gender?: string;
  age_min?: number;
  age_max?: number;
  skip?: number;
  limit?: number;
  sort_by?: string;
  sort_order?: string;
}

interface PatientSearchResult {
  patient_id: number;
  full_name: string;
  email?: string;
  phone_number?: string;
  date_of_birth?: string;
  gender?: string;
  identification_id?: string;
  health_insurance_card_no?: string;
  assigned_doctor_id?: number;
  assigned_doctor_name?: string;
  age?: number;
}

interface PatientSearchResponse {
  patients: PatientSearchResult[];
  total_count: number;
  page: number;
  per_page: number;
  total_pages: number;
}

const PatientSearch: React.FC = () => {
  const [searchParams, setSearchParams] = useState<PatientSearchQuery>({
    limit: 10,
    skip: 0,
    sort_by: "full_name",
    sort_order: "asc"
  });
  const [searchResults, setSearchResults] = useState<PatientSearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedPatient, setSelectedPatient] = useState<PatientSearchResult | null>(null);
  const [showAdvancedSearch, setShowAdvancedSearch] = useState(false);

  // Current user role for access control display
  const [userRole, setUserRole] = useState<string>('');

  useEffect(() => {
    const role = localStorage.getItem('role') || '';
    setUserRole(role);
  }, []);

  const handleSearch = async (page: number = 1) => {
    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('accessToken');
      if (!token) {
        throw new Error('Authentication token not found');
      }

      // Calculate skip based on page
      const skip = (page - 1) * (searchParams.limit || 10);
      
      const searchPayload: PatientSearchQuery = {
        ...searchParams,
        skip
      };

      // Remove empty values
      Object.keys(searchPayload).forEach(key => {
        const value = searchPayload[key as keyof PatientSearchQuery];
        if (value === '' || value === null || value === undefined) {
          delete searchPayload[key as keyof PatientSearchQuery];
        }
      });

      console.log('Search payload:', searchPayload);

      const response = await axios.post(
        `${BACKEND_URL}/patients/search`,
        searchPayload,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      setSearchResults(response.data);
      console.log('Search results:', response.data);
    } catch (err) {
      console.error('Search error:', err);
      if (axios.isAxiosError(err)) {
        if (err.response?.status === 401) {
          setError('Authentication failed. Please log in again.');
        } else if (err.response?.status === 403) {
          setError('You do not have permission to search patients.');
        } else {
          setError(`Search failed: ${err.response?.data?.detail || err.message}`);
        }
      } else {
        setError('An unexpected error occurred during search.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    
    let processedValue: any = value;
    
    // Handle different input types
    if (type === 'number') {
      processedValue = value === '' ? undefined : Number(value);
    } else if (type === 'checkbox') {
      processedValue = (e.target as HTMLInputElement).checked;
    } else if (value === '') {
      processedValue = undefined;
    }

    setSearchParams(prev => ({
      ...prev,
      [name]: processedValue
    }));
  };

  const handlePageChange = (newPage: number) => {
    handleSearch(newPage);
  };

  const clearSearch = () => {
    setSearchParams({
      limit: 10,
      skip: 0,
      sort_by: "full_name",
      sort_order: "asc"
    });
    setSearchResults(null);
    setError(null);
    setSelectedPatient(null);
  };

  const handlePatientSelect = (patient: PatientSearchResult) => {
    setSelectedPatient(patient);
  };

  const closePatientDetails = () => {
    setSelectedPatient(null);
  };

  return (
    <div className="patient-search-container">
      <div className="search-header">
        <h2>Patient Search</h2>
        <p className="role-info">
          Searching as: <strong>{userRole}</strong>
          {userRole === 'DOCTOR' && ' (You can only see your assigned patients)'}
          {userRole === 'PATIENT' && ' (You can only see your own record)'}
        </p>
      </div>

      {/* Search Form */}
      <div className="search-form">
        <div className="basic-search">
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="query">General Search</label>
              <input
                type="text"
                id="query"
                name="query"
                value={searchParams.query || ''}
                onChange={handleInputChange}
                placeholder="Search by name, email, phone, or address..."
                className="search-input"
              />
            </div>
            <div className="form-group">
              <label htmlFor="limit">Results per page</label>
              <select
                id="limit"
                name="limit"
                value={searchParams.limit || 10}
                onChange={handleInputChange}
                className="select-input"
              >
                <option value={5}>5</option>
                <option value={10}>10</option>
                <option value={25}>25</option>
                <option value={50}>50</option>
              </select>
            </div>
          </div>
        </div>

        {/* Advanced Search Toggle */}
        <button
          type="button"
          className="toggle-advanced"
          onClick={() => setShowAdvancedSearch(!showAdvancedSearch)}
        >
          {showAdvancedSearch ? 'Hide' : 'Show'} Advanced Search
        </button>

        {/* Advanced Search Fields */}
        {showAdvancedSearch && (
          <div className="advanced-search">
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="full_name">Full Name</label>
                <input
                  type="text"
                  id="full_name"
                  name="full_name"
                  value={searchParams.full_name || ''}
                  onChange={handleInputChange}
                  placeholder="Patient full name"
                />
              </div>
              <div className="form-group">
                <label htmlFor="email">Email</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={searchParams.email || ''}
                  onChange={handleInputChange}
                  placeholder="Patient email"
                />
              </div>
              <div className="form-group">
                <label htmlFor="phone_number">Phone</label>
                <input
                  type="text"
                  id="phone_number"
                  name="phone_number"
                  value={searchParams.phone_number || ''}
                  onChange={handleInputChange}
                  placeholder="Phone number"
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="patient_id">Patient ID</label>
                <input
                  type="number"
                  id="patient_id"
                  name="patient_id"
                  value={searchParams.patient_id || ''}
                  onChange={handleInputChange}
                  placeholder="Patient ID number"
                />
              </div>
              <div className="form-group">
                <label htmlFor="age_min">Min Age</label>
                <input
                  type="number"
                  id="age_min"
                  name="age_min"
                  value={searchParams.age_min || ''}
                  onChange={handleInputChange}
                  placeholder="Minimum age"
                  min="0"
                />
              </div>
              <div className="form-group">
                <label htmlFor="age_max">Max Age</label>
                <input
                  type="number"
                  id="age_max"
                  name="age_max"
                  value={searchParams.age_max || ''}
                  onChange={handleInputChange}
                  placeholder="Maximum age"
                  min="0"
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="gender">Gender</label>
                <select
                  id="gender"
                  name="gender"
                  value={searchParams.gender || ''}
                  onChange={handleInputChange}
                >
                  <option value="">Any Gender</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <div className="form-group">
                <label htmlFor="identification_id">ID Number</label>
                <input
                  type="text"
                  id="identification_id"
                  name="identification_id"
                  value={searchParams.identification_id || ''}
                  onChange={handleInputChange}
                  placeholder="Identification ID"
                />
              </div>
              <div className="form-group">
                <label htmlFor="health_insurance_card_no">Insurance Card</label>
                <input
                  type="text"
                  id="health_insurance_card_no"
                  name="health_insurance_card_no"
                  value={searchParams.health_insurance_card_no || ''}
                  onChange={handleInputChange}
                  placeholder="Health insurance card number"
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="assigned_doctor_id">Assigned Doctor ID</label>
                <input
                  type="number"
                  id="assigned_doctor_id"
                  name="assigned_doctor_id"
                  value={searchParams.assigned_doctor_id || ''}
                  onChange={handleInputChange}
                  placeholder="Doctor ID"
                />
              </div>
              <div className="form-group">
                <label htmlFor="sort_by">Sort By</label>
                <select
                  id="sort_by"
                  name="sort_by"
                  value={searchParams.sort_by || 'full_name'}
                  onChange={handleInputChange}
                >
                  <option value="full_name">Full Name</option>
                  <option value="date_of_birth">Date of Birth</option>
                  <option value="patient_id">Patient ID</option>
                </select>
              </div>
              <div className="form-group">
                <label htmlFor="sort_order">Sort Order</label>
                <select
                  id="sort_order"
                  name="sort_order"
                  value={searchParams.sort_order || 'asc'}
                  onChange={handleInputChange}
                >
                  <option value="asc">Ascending</option>
                  <option value="desc">Descending</option>
                </select>
              </div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="search-actions">
          <button
            type="button"
            className="search-btn"
            onClick={() => handleSearch(1)}
            disabled={loading}
          >
            {loading ? 'Searching...' : 'Search Patients'}
          </button>
          <button
            type="button"
            className="clear-btn"
            onClick={clearSearch}
            disabled={loading}
          >
            Clear
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="error-message">
          <p>{error}</p>
        </div>
      )}

      {/* Search Results */}
      {searchResults && (
        <div className="search-results">
          <div className="results-header">
            <h3>Search Results</h3>
            <p>
              Found {searchResults.total_count} patient{searchResults.total_count !== 1 ? 's' : ''} 
              (Page {searchResults.page} of {searchResults.total_pages})
            </p>
          </div>

          {searchResults.patients.length === 0 ? (
            <div className="no-results">
              <p>No patients found matching your search criteria.</p>
            </div>
          ) : (
            <>
              <div className="results-table">
                <table>
                  <thead>
                    <tr>
                      <th>Patient ID</th>
                      <th>Name</th>
                      <th>Email</th>
                      <th>Phone</th>
                      <th>Age</th>
                      <th>Gender</th>
                      <th>Doctor</th>
                      <th>Date of Birth</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {searchResults.patients.map((patient) => (
                      <tr key={patient.patient_id}>
                        <td>{patient.patient_id}</td>
                        <td>{patient.full_name}</td>
                        <td>{patient.email || 'N/A'}</td>
                        <td>{patient.phone_number || 'N/A'}</td>
                        <td>{patient.age || 'N/A'}</td>
                        <td>{patient.gender || 'N/A'}</td>
                        <td>{patient.assigned_doctor_name || 'Unassigned'}</td>
                        <td>{patient.date_of_birth ? new Date(patient.date_of_birth).toLocaleDateString() : 'N/A'}</td>
                        <td>
                          <button
                            className="view-btn"
                            onClick={() => handlePatientSelect(patient)}
                          >
                            View
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              {searchResults.total_pages > 1 && (
                <div className="pagination">
                  <button
                    className="page-btn"
                    onClick={() => handlePageChange(searchResults.page - 1)}
                    disabled={searchResults.page <= 1 || loading}
                  >
                    Previous
                  </button>
                  
                  <span className="page-info">
                    Page {searchResults.page} of {searchResults.total_pages}
                  </span>
                  
                  <button
                    className="page-btn"
                    onClick={() => handlePageChange(searchResults.page + 1)}
                    disabled={searchResults.page >= searchResults.total_pages || loading}
                  >
                    Next
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      )}

      {/* Patient Details Modal */}
      {selectedPatient && (
        <div className="modal-overlay" onClick={closePatientDetails}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Patient Details</h3>
              <button className="close-btn" onClick={closePatientDetails}>×</button>
            </div>
            <div className="modal-body">
              <div className="patient-details">
                <div className="detail-row">
                  <strong>Patient ID:</strong> {selectedPatient.patient_id}
                </div>
                <div className="detail-row">
                  <strong>Full Name:</strong> {selectedPatient.full_name}
                </div>
                <div className="detail-row">
                  <strong>Email:</strong> {selectedPatient.email || 'N/A'}
                </div>
                <div className="detail-row">
                  <strong>Phone:</strong> {selectedPatient.phone_number || 'N/A'}
                </div>
                <div className="detail-row">
                  <strong>Date of Birth:</strong> {selectedPatient.date_of_birth ? new Date(selectedPatient.date_of_birth).toLocaleDateString() : 'N/A'}
                </div>
                <div className="detail-row">
                  <strong>Age:</strong> {selectedPatient.age || 'N/A'}
                </div>
                <div className="detail-row">
                  <strong>Gender:</strong> {selectedPatient.gender || 'N/A'}
                </div>
                <div className="detail-row">
                  <strong>Identification ID:</strong> {selectedPatient.identification_id || 'N/A'}
                </div>
                <div className="detail-row">
                  <strong>Health Insurance Card:</strong> {selectedPatient.health_insurance_card_no || 'N/A'}
                </div>
                <div className="detail-row">
                  <strong>Assigned Doctor:</strong> {selectedPatient.assigned_doctor_name || 'Unassigned'}
                </div>
                <div className="detail-row">
                  <strong>Assigned Doctor ID:</strong> {selectedPatient.assigned_doctor_id || 'N/A'}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PatientSearch;
