import React, { useState, useEffect } from 'react';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { DateCalendar } from '@mui/x-date-pickers/DateCalendar';
import { Badge, CircularProgress, Modal, Box, Button, TextField, MenuItem, Select } from '@mui/material';
import { PickersDay, PickersDayProps } from '@mui/x-date-pickers/PickersDay';
import dayjs, { Dayjs } from 'dayjs';
import { toast } from 'react-toastify';
import 'dayjs/locale/vi'; // Import Vietnamese locale
import axios from 'axios';
import './viewAppointment.css'; // Import the CSS file for styling

const BACKEND_URL = (process.env.REACT_APP_BACKEND_URL || '').replace(/\/+$/, '');

type Appointment = {
  patient_id: number;
  doctor_id: number;
  appointment_time: string;
  appointment_day: string;
  reason: string;
  appointment_id: number;
  doctorName?: string;
};

const ViewAppointment = () => {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedDate, setSelectedDate] = useState(dayjs());
  const [selectedAppointment, setSelectedAppointment] = useState<Appointment | null>(null);
  const [rescheduleDate, setRescheduleDate] = useState('');
  const [rescheduleTime, setRescheduleTime] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [showRescheduleFields, setShowRescheduleFields] = useState(false);

  const availableTimes = ['08:30', '09:30', '10:30', '13:30', '14:30', '15:30', '16:30']; // Predefined times

  useEffect(() => {
    const fetchAppointments = async () => {
      try {
        const token = localStorage.getItem('accessToken');
        const response = await axios.get(`${BACKEND_URL}/appointments/me`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        const today = new Date().toISOString().split('T')[0];
        const upcomingAppointments = response.data.filter(
          (appointment: Appointment) => appointment.appointment_day >= today
        );

        const appointmentsWithDoctorNames = await Promise.all(
          upcomingAppointments.map(async (appointment: Appointment) => {
            try {
              const doctorResponse = await axios.get(`${BACKEND_URL}/doctors/${appointment.doctor_id}`, {
                headers: {
                  Authorization: `Bearer ${token}`,
                },
              });
              return {
                ...appointment,
                doctorName: doctorResponse.data.doctor_name,
              };
            } catch (err) {
              console.error(`Failed to fetch doctor name for doctor_id ${appointment.doctor_id}:`, err);
              return {
                ...appointment,
                doctorName: 'Bác sĩ không xác định',
              };
            }
          })
        );

        appointmentsWithDoctorNames.sort((a, b) => {
          const dateA = new Date(`${a.appointment_day}T${a.appointment_time}`);
          const dateB = new Date(`${b.appointment_day}T${b.appointment_time}`);
          return dateA.getTime() - dateB.getTime();
        });

        setAppointments(appointmentsWithDoctorNames);
      } catch (err) {
        console.error('Failed to fetch appointments:', err);
        setError('Không thể tải danh sách lịch hẹn.');
      } finally {
        setLoading(false);
      }
    };

    fetchAppointments();
  }, []);

  const handleAppointmentClick = (appointment: Appointment) => {
    setSelectedAppointment(appointment);
    setModalOpen(true);
  };

  const handleCancelAppointment = async () => {
    if (!selectedAppointment) return;

    try {
      const token = localStorage.getItem('accessToken');
      await axios.delete(`${BACKEND_URL}/appointments/${selectedAppointment.appointment_id}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setAppointments((prev) =>
        prev.filter((appointment) => appointment.appointment_id !== selectedAppointment.appointment_id)
      );
      setModalOpen(false);
    } catch (err) {
      console.error('Failed to cancel appointment:', err);
      setError('Không thể hủy lịch hẹn.');
      throw new Error('Failed to cancel appointment.');
    }
  };

  const handleRescheduleAppointment = async () => {
    if (!selectedAppointment || !rescheduleDate || !rescheduleTime) return;

    try {
      const token = localStorage.getItem('accessToken');
      await axios.put(
        `${BACKEND_URL}/appointments/${selectedAppointment.appointment_id}`,
        {
          appointment_day: rescheduleDate,
          appointment_time: rescheduleTime,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      setAppointments((prev) =>
        prev.map((appointment) =>
          appointment.appointment_id === selectedAppointment.appointment_id
            ? { ...appointment, appointment_day: rescheduleDate, appointment_time: rescheduleTime }
            : appointment
        )
      );
      setModalOpen(false);
    } catch (err) {
      console.error('Failed to reschedule appointment:', err);
      setError('Không thể thay đổi lịch hẹn.');
      throw new Error('Failed to reschedule appointment.');
    }
  };

  const handleToggleReschedule = () => {
    setShowRescheduleFields((prev) => !prev);
  };

  const filteredAppointments = appointments.filter((appointment) =>
    dayjs(appointment.appointment_day).isSame(selectedDate, 'day')
  );

  const appointmentDates = appointments.map((appointment) => appointment.appointment_day);

  const CustomDay = (props: PickersDayProps) => {
    const { day, outsideCurrentMonth, ...other } = props;
    const dateString = day.format('YYYY-MM-DD');
    const hasAppointment = appointmentDates.includes(dateString);

    return (
      <Badge
        key={dateString}
        overlap="circular"
        badgeContent={hasAppointment ? <span className="appointment-dot" /> : undefined}
      >
        <PickersDay day={day} outsideCurrentMonth={outsideCurrentMonth} {...other} />
      </Badge>
    );
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDayjs} adapterLocale="vi">
      <div className="appointments-container">
        <h1 className="appointments-header">Lịch hẹn sắp tới</h1>

        {loading ? (
          <div className="loading-spinner">
            <CircularProgress />
            <p>Đang tải...</p>
          </div>
        ) : (
          <DateCalendar
            value={selectedDate}
            onChange={(newValue: Dayjs | null) => {
              if (newValue) setSelectedDate(newValue);
            }}
            views={['year', 'month', 'day']}
            slots={{ day: CustomDay }}
          />
        )}

        {!loading && filteredAppointments.length > 0 ? (
          <table className="appointments-table">
            <thead>
              <tr>
                <th>Giờ</th>
                <th>Bác sĩ</th>
                <th>Lý do</th>
              </tr>
            </thead>
            <tbody>
              {filteredAppointments.map((appointment) => (
                <tr
                  key={appointment.appointment_id}
                  onClick={() => handleAppointmentClick(appointment)}
                  className="clickable-row"
                >
                  <td>{appointment.appointment_time}</td>
                  <td>{appointment.doctorName}</td>
                  <td>{appointment.reason}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          !loading && <p>Không có lịch hẹn nào trong ngày này.</p>
        )}

        <Modal open={modalOpen} onClose={() => setModalOpen(false)}>
          <Box className="appointment-modal">
            <h2>Thao tác với lịch hẹn</h2>
            {selectedAppointment && (
                <>
                  <p><strong>Bác sĩ:</strong> {selectedAppointment.doctorName}</p>
                  <p><strong>Ngày:</strong> {selectedAppointment.appointment_day}</p>
                  <p><strong>Giờ:</strong> {selectedAppointment.appointment_time}</p>

                  {error && (
                  <Box mt={2} color="error.main">
                    <p style={{ color: 'red', margin: 0 }}>{error}</p>
                  </Box>
                  )}

                  <Box display="flex" alignItems="center" gap={2} mt={2}>
                  <Button
                    variant="contained"
                    color="error"
                    onClick={async () => {
                      try {
                        await handleCancelAppointment();
                        toast.success('Hủy lịch hẹn thành công!');
                      } catch (err) {
                        console.error('Failed to cancel appointment:', err);
                      }
                    }}
                    sx={{ height: 40 }}
                  >
                    Hủy lịch hẹn
                  </Button>

                  <Button
                    variant="outlined"
                    color="primary"
                    onClick={handleToggleReschedule}
                    sx={{ height: 40 }}
                  >
                    {showRescheduleFields ? "Ẩn thay đổi lịch" : "Thay đổi lịch"}
                  </Button>
                  </Box>
                  {showRescheduleFields && (
                  <div className="reschedule-section">
                    <h2 className="reschedule-title">Thay đổi lịch hẹn</h2>

                    <div className="form-group">
                    <label htmlFor="reschedule-date">Ngày mới</label>
                    <input
                      id="reschedule-date"
                      type="date"
                      value={rescheduleDate}
                      onChange={(e) => setRescheduleDate(e.target.value)}
                    />
                    </div>

                    <div className="form-group">
                    <label htmlFor="reschedule-time">Giờ mới</label>
                    <select
                      id="reschedule-time"
                      value={rescheduleTime}
                      onChange={(e) => setRescheduleTime(e.target.value)}
                    >
                      <option value="" disabled>
                      Chọn giờ
                      </option>
                      {availableTimes.map((time) => (
                      <option key={time} value={time}>
                        {time}
                      </option>
                      ))}
                    </select>
                    </div>

                    <button
                    className="confirm-button"
                    onClick={async () => {
                      try {
                        await handleRescheduleAppointment();
                        toast.success('Thay đổi lịch hẹn thành công!');
                      } catch (err) {
                        console.error('Failed to reschedule appointment:', err);
                      }
                    }}
                    >
                    Xác nhận thay đổi
                    </button>
                  </div>
                  )}
                </>
            )}
          </Box>
        </Modal>
      </div>
    </LocalizationProvider>
  );
};

export default ViewAppointment;