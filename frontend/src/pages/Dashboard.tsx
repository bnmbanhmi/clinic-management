// pages/Dashboard.tsx
import React from 'react';

import { Routes, Route } from 'react-router-dom';

import {UserRole} from '../types/UserType'; // Adjust the import path as necessary

import BaseDashboard from '../components/layout/BaseDashboard';
import DoctorDashboard from '../components/dashboards/DoctorDashboard';
import PatientDashboard from '../components/dashboards/PatientDashboard';
import StaffDashboard from '../components/dashboards/StaffDashboard';
import AdminDashboard from '../components/dashboards/AdminDashboard';
import BookAppointment from '../components/appointment/BookAppointment';
import PatientSearch from '../components/patients/PatientSearch';

type Props = {
  role: UserRole;
};

/**
 * Dashboard component renders the appropriate dashboard layout
 * based on the user's role. It supports roles such as 'doctor', 'patient',
 * 'staff', and 'admin'.
 */
const Dashboard: React.FC<Props> = ({ role }) => {
  const renderDashboard = () => {
    const dashboardMap: Record<Props['role'], React.ReactNode> = {
      DOCTOR: <DoctorDashboard />,
      PATIENT: <PatientDashboard />,
      CLINIC_STAFF: <StaffDashboard />,
      ADMIN: <AdminDashboard />,
    };

    if (!dashboardMap[role]) {
      console.warn(`Unsupported role encountered: ${role}`);
      return null;
    }

    return dashboardMap[role];
  };

  return (
    <BaseDashboard role={role}>
      <Routes>
        <Route path="/" element={renderDashboard()} />
        <Route path="appointments/book" element={<BookAppointment />} />
        <Route path="patients" element={<PatientSearch />} />
        {/* <Route path="appointments" element={<Appointments />} />
        <Route path="prescriptions" element={<Prescriptions />} />
        <Route path="records" element={<MedicalHistory />} /> */}
      </Routes>
    </BaseDashboard>
  );
};

export default Dashboard;
