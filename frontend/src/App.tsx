import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import LoginPage from './components/LoginPage';
import DashboardPage from './components/DashboardPage'; // Import DashboardPage
import ForgotPasswordPage from './components/ForgotPasswordPage'; // Import ForgotPasswordPage
import ResetPasswordPage from './components/ResetPasswordPage'; // Import ResetPasswordPage

// A simple HOC for protected routes
const ProtectedRoute: React.FC<{ children: React.ReactElement }> = ({ children }) => {
  const isAuthenticated = !!localStorage.getItem('accessToken');
  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/reset-password" element={<ResetPasswordPage />} />
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          {/* Redirect root to login or dashboard based on auth state */}
          <Route 
            path="/" 
            element={localStorage.getItem('accessToken') ? <Navigate to="/dashboard" replace /> : <Navigate to="/login" replace />}
          />
          {/* You can add a 404 page here if needed */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
