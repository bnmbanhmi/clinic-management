import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom'; // Import useNavigate and Link

const LoginPage: React.FC = () => {
    // const { t } = useTranslation(); // Initialize translation function
    const t = (key: string, params?: object) => { // Placeholder t function
        if (params) {
            let message = key;
            for (const [paramKey, value] of Object.entries(params)) {
                message = message.replace(`{{${paramKey}}}`, String(value));
            }
            return message;
        }
        return key;
    };

    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate(); // Initialize useNavigate

    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setError('');
        setLoading(true);

        try {
            const formData = new URLSearchParams();
            formData.append('username', username);
            formData.append('password', password);

            const response = await axios.post('http://127.0.0.1:8000/auth/token', formData, {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
            });

            if (response.data.access_token) {
                localStorage.setItem('accessToken', response.data.access_token);
                navigate('/dashboard');
            }
        } catch (err: any) {
            if (axios.isAxiosError(err) && err.response) {
                if (err.response.status === 401 || err.response.status === 403) {
                    setError('Tên đăng nhập hoặc mật khẩu không đúng, hoặc vai trò không được phép.');
                } else {
                    setError(`Đăng nhập thất bại: ${err.response.data.detail || 'Lỗi máy chủ'}`);
                }
            } else {
                setError('Đăng nhập thất bại. Đã xảy ra lỗi không mong muốn.');
            }
            console.error("Login error:", err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', padding: '20px', boxSizing: 'border-box' }}>
            <h2>Đăng nhập Phần mềm Quản lý phòng khám</h2>
            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', width: '100%', maxWidth: '320px', gap: '12px', padding: '20px', border: '1px solid #ccc', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
                <div>
                    <label htmlFor="username" style={{ marginBottom: '4px', display: 'block' }}>Tên đăng nhập:</label>
                    <input
                        type="text"
                        id="username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                        style={{ width: '100%', padding: '10px', boxSizing: 'border-box', border: '1px solid #ccc', borderRadius: '4px' }}
                    />
                </div>
                <div>
                    <label htmlFor="password" style={{ marginBottom: '4px', display: 'block' }}>Mật khẩu:</label>
                    <input
                        type="password"
                        id="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                        style={{ width: '100%', padding: '10px', boxSizing: 'border-box', border: '1px solid #ccc', borderRadius: '4px' }}
                    />
                </div>
                {error && <p style={{ color: 'red', textAlign: 'center', margin: '0' }}>{error}</p>}
                <button type="submit" disabled={loading} style={{ padding: '10px 15px', cursor: 'pointer', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', fontSize: '16px' }}>
                    {loading ? 'Đang đăng nhập...' : 'Đăng nhập'}
                </button>
                <div style={{ textAlign: 'center', marginTop: '10px' }}>
                    <Link to="/forgot-password">Quên mật khẩu?</Link>
                </div>
            </form>
        </div>
    );
};

export default LoginPage;
