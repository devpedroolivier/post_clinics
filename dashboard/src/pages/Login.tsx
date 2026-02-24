import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Lock } from 'lucide-react';
import { loginCall } from '../services/api';

export const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        try {
            const data = await loginCall({ username, password });
            const token = data.access_token || data.token;
            if (token) {
                localStorage.setItem('token', token);
                navigate('/');
            }
        } catch (err: any) {
            setError('Acesso negado. Verifique suas credenciais.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-brand-bg relative overflow-hidden">
            {/* Subtle Background Elements */}
            <div className="absolute top-[-20%] left-[-10%] w-[500px] h-[500px] bg-blue-50 rounded-full blur-3xl opacity-50 z-0"></div>
            <div className="absolute bottom-[-10%] right-[-10%] w-[400px] h-[400px] bg-blue-50/50 rounded-full blur-3xl opacity-50 z-0"></div>

            <div className="card w-full max-w-md p-8 sm:p-12 z-10 shadow-xl border-brand-border/50 relative">
                <div className="mb-8 text-center">
                    <div className="w-12 h-12 bg-black text-white rounded-xl flex items-center justify-center mx-auto mb-4 shadow-md">
                        <Lock size={24} />
                    </div>
                    <h1 className="text-2xl font-bold tracking-tight text-brand-text-primary">POST Clinics</h1>
                    <p className="text-brand-text-secondary mt-2 text-sm">Painel Administrativo Restrito</p>
                </div>

                {error && (
                    <div className="mb-6 p-3 bg-red-50 text-brand-danger text-sm font-medium rounded-lg border border-red-100/50 text-center animate-[slideUp_0.2s_ease-out]">
                        {error}
                    </div>
                )}

                <form onSubmit={handleLogin} className="space-y-5">
                    <div>
                        <label className="form-label">Usuário</label>
                        <input
                            type="text"
                            required
                            className="input-field shadow-sm bg-gray-50/50 focus:bg-white"
                            placeholder="ex: admin"
                            value={username}
                            onChange={e => setUsername(e.target.value)}
                        />
                    </div>
                    <div>
                        <label className="form-label">Senha</label>
                        <input
                            type="password"
                            required
                            className="input-field shadow-sm bg-gray-50/50 focus:bg-white"
                            placeholder="••••••••"
                            value={password}
                            onChange={e => setPassword(e.target.value)}
                        />
                    </div>
                    <div className="pt-2">
                        <button
                            type="submit"
                            disabled={loading}
                            className="btn-primary w-full py-2.5 shadow-md flex justify-center items-center"
                        >
                            {loading ? (
                                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                            ) : (
                                'Entrar no Sistema'
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};
