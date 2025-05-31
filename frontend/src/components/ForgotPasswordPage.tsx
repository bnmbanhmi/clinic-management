import React, { useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

const ForgotPasswordPage: React.FC = () => {
    const [email, setEmail] = useState('');
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setError('');
        setMessage('');
        setLoading(true);

        try {
            const response = await axios.post('http://127.0.0.1:8000/password/forgot-password', { email });
            setMessage(response.data.message);
        } catch (err: any) {
            if (axios.isAxiosError(err) && err.response) {
                setError(err.response.data.detail || 'Failed to send reset link. Please try again.');
            } else {
                setError('An unexpected error occurred. Please try again.');
            }
            console.error("Forgot password error:", err);
        }
        setLoading(false);
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', padding: '20px', boxSizing: 'border-box' }}>
            <h2>Quên mật khẩu</h2>
            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', width: '100%', maxWidth: '320px', gap: '12px', padding: '20px', border: '1px solid #ccc', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
                <p style={{ textAlign: 'center', margin: '0 0 16px 0' }}>Nhập địa chỉ email của bạn để nhận liên kết đặt lại mật khẩu.</p>
                <div>
                    <label htmlFor="email" style={{ marginBottom: '4px', display: 'block' }}>Email:</label>
                    <input
                        type="email"
                        id="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                        style={{ width: '100%', padding: '10px', boxSizing: 'border-box', border: '1px solid #ccc', borderRadius: '4px' }}
                    />
                </div>
                {message && <p style={{ color: 'green', textAlign: 'center', margin: '0' }}>{message}</p>}
                {error && <p style={{ color: 'red', textAlign: 'center', margin: '0' }}>{error}</p>}
                <button type="submit" disabled={loading} style={{ padding: '10px 15px', cursor: 'pointer', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', fontSize: '16px' }}>
                    {loading ? 'Đang gửi...' : 'Gửi liên kết đặt lại'}
                </button>
            </form>
            <div style={{ marginTop: '16px' }}>
                <Link to="/login" style={{ color: '#007bff', textDecoration: 'none' }}>Quay lại Đăng nhập</Link>
            </div>
        </div>
    );
};

export default ForgotPasswordPage;
