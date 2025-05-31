import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

// Placeholder translation function
const t = (key: string, params?: object) => {
    if (params) {
        let message = key;
        for (const [paramKey, value] of Object.entries(params)) {
            message = message.replace(`{{${paramKey}}}`, String(value));
        }
        return message;
    }
    return key;
};

const RegisterPage: React.FC = () => {
    const [username, setUsername] = useState('');
    const [mail, setMail] = useState('');
    const [password, setPassword] = useState('');
    const [fullname, setFullname] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setError('');
        setLoading(true);

        try {
            const formData = new URLSearchParams();
            formData.append('username', username);
            formData.append('password', password);
            formData.append('mail', mail);
            formData.append('fullname', fullname);

            const response = await axios.post('http://127.0.0.1:8000/auth/register', {
                username,
                email: mail,
                password,
                full_name: fullname,
            }, {
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (response.status === 201 || response.status === 200) {
                navigate('/login');
            }
        } catch (err: any) {
            if (axios.isAxiosError(err) && err.response) {
                const detail = err.response.data.detail;

                if (Array.isArray(detail)) {
                    // Join all error messages into a single string
                    setError(detail.map((e: any) => e.msg).join(' | '));
                } else {
                    setError(detail || 'Đăng ký thất bại. Vui lòng kiểm tra lại thông tin.');
                }
            }
            console.error("Register error:", err);
        } finally {
            setLoading(false);
        }
    };

    const handleLogin = () => {
        navigate('/login');
    };

    return (
        <div style={styles.container}>
            <div style={styles.card}>
                <h2 style={styles.heading}>Đăng ký tài khoản</h2>
                <p style={styles.subHeading}>Tạo tài khoản bệnh nhân</p>

                <form onSubmit={handleSubmit} style={styles.form}>
                    <div style={styles.formGroup}>
                        <label htmlFor="username" style={styles.label}>Tên đăng nhập</label>
                        <input
                            type="text"
                            id="username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                            style={styles.input}
                            placeholder="Nhập tên đăng nhập"
                        />
                    </div>

                    <div style={styles.formGroup}>
                        <label htmlFor="mail" style={styles.label}>Email</label>
                        <input
                            type="email"
                            id="mail"
                            value={mail}
                            onChange={(e) => setMail(e.target.value)}
                            required
                            style={styles.input}
                            placeholder="Nhập email"
                        />
                    </div>

                    <div style={styles.formGroup}>
                        <label htmlFor="fullname" style={styles.label}>Họ và tên</label>
                        <input
                            type="text"
                            id="fullname"
                            value={fullname}
                            onChange={(e) => setFullname(e.target.value)}
                            required
                            style={styles.input}
                            placeholder="Nhập họ và tên"
                        />
                    </div>

                    <div style={styles.formGroup}>
                        <label htmlFor="password" style={styles.label}>Mật khẩu</label>
                        <input
                            type="password"
                            id="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            style={styles.input}
                            placeholder="Nhập mật khẩu"
                        />
                    </div>

                    {error && (
                        <p style={styles.errorText}>{error}</p>
                    )}

                    <button
                        type="submit"
                        disabled={loading}
                        style={{ ...styles.button, backgroundColor: '#28a745' }}
                    >
                        {loading ? 'Đang đăng ký...' : 'Đăng ký'}
                    </button>

                    <button
                        type="button"
                        onClick={handleLogin}
                        style={{ ...styles.button, backgroundColor: '#6c757d' }}
                    >
                        Đã có tài khoản? Đăng nhập
                    </button>
                </form>
            </div>
        </div>
    );
};

const styles: { [key: string]: React.CSSProperties } = {
    container: {
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        background: 'linear-gradient(to right, #eef2f3, #8e9eab)',
        padding: '20px',
    },
    card: {
        backgroundColor: '#ffffff',
        borderRadius: '12px',
        boxShadow: '0 10px 25px rgba(0, 0, 0, 0.1)',
        padding: '32px',
        maxWidth: '400px',
        width: '100%',
        boxSizing: 'border-box',
    },
    heading: {
        textAlign: 'center',
        marginBottom: '12px',
        fontSize: '24px',
        fontWeight: 'bold',
        color: '#333',
    },
    subHeading: {
        textAlign: 'center',
        marginBottom: '24px',
        color: '#666',
        fontSize: '14px',
    },
    form: {
        display: 'flex',
        flexDirection: 'column',
        gap: '16px',
    },
    formGroup: {
        display: 'flex',
        flexDirection: 'column',
    },
    label: {
        marginBottom: '6px',
        fontWeight: 500,
        color: '#333',
    },
    input: {
        padding: '10px 12px',
        border: '1px solid #ccc',
        borderRadius: '6px',
        fontSize: '14px',
        outlineColor: '#007bff',
    },
    button: {
        padding: '12px',
        color: '#fff',
        fontSize: '15px',
        border: 'none',
        borderRadius: '6px',
        cursor: 'pointer',
        transition: 'background-color 0.2s',
    },
    errorText: {
        color: 'red',
        fontSize: '14px',
        textAlign: 'center',
        marginTop: '-8px',
        marginBottom: '8px',
    },
};

export default RegisterPage;