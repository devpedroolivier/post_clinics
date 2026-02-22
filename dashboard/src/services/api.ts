export const API_BASE_URL = import.meta.env.DEV ? 'http://localhost:8000' : '';

const getHeaders = () => {
    const token = localStorage.getItem('token');
    return {
        'Content-Type': 'application/json',
        'ngrok-skip-browser-warning': 'true',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
    };
};

export const loginCall = async (credentials: any) => {
    const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials)
    });
    if (!response.ok) throw new Error('Invalid credentials');
    return response.json();
};

export const fetchAppointments = async () => {
    const response = await fetch(`${API_BASE_URL}/api/appointments`, {
        headers: getHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch appointments');
    return response.json();
};

export const createAppointment = async (payload: any) => {
    const response = await fetch(`${API_BASE_URL}/api/appointments`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify(payload)
    });
    if (!response.ok) throw new Error('Failed to create appointment');
    return response.json();
};

export const updateAppointment = async (id: string, payload: any) => {
    const response = await fetch(`${API_BASE_URL}/api/appointments/${id}`, {
        method: 'PUT',
        headers: getHeaders(),
        body: JSON.stringify(payload)
    });
    if (!response.ok) throw new Error('Failed to update appointment');
    return response.json();
};

export const deleteAppointment = async (id: string) => {
    const response = await fetch(`${API_BASE_URL}/api/appointments/${id}`, {
        method: 'DELETE',
        headers: getHeaders()
    });
    if (!response.ok) throw new Error('Failed to delete appointment');
    return response.json();
};
