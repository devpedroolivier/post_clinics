export const API_BASE_URL = import.meta.env.DEV ? 'http://localhost:8000' : '';

export const fetchAppointments = async () => {
    const response = await fetch(`${API_BASE_URL}/api/appointments`, {
        headers: {
            'ngrok-skip-browser-warning': 'true'
        }
    });
    if (!response.ok) {
        throw new Error('Failed to fetch appointments');
    }
    return response.json();
};
export const createAppointment = async (payload: any) => {
    const response = await fetch(`${API_BASE_URL}/api/appointments`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'ngrok-skip-browser-warning': 'true'
        },
        body: JSON.stringify(payload)
    });
    if (!response.ok) throw new Error('Failed to create appointment');
    return response.json();
};

export const updateAppointment = async (id: string, payload: any) => {
    const response = await fetch(`${API_BASE_URL}/api/appointments/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'ngrok-skip-browser-warning': 'true'
        },
        body: JSON.stringify(payload)
    });
    if (!response.ok) throw new Error('Failed to update appointment');
    return response.json();
};

export const deleteAppointment = async (id: string) => {
    const response = await fetch(`${API_BASE_URL}/api/appointments/${id}`, {
        method: 'DELETE',
        headers: {
            'ngrok-skip-browser-warning': 'true'
        }
    });
    if (!response.ok) throw new Error('Failed to delete appointment');
    return response.json();
};
