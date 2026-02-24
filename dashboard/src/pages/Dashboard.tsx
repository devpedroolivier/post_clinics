import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import listPlugin from '@fullcalendar/list';
import interactionPlugin from '@fullcalendar/interaction';

import { Sidebar } from '../components/Sidebar';

import { Toast } from '../components/Toast';

import { fetchAppointments, createAppointment, updateAppointment, deleteAppointment } from '../services/api';

type Appointment = {
    id: string;
    patient_name: string;
    patient_phone: string;
    datetime: string;
    service: string;
    professional: string;
    status: string;
};

// Custom Event Render for Minimalist UI
function renderEventContent(eventInfo: any) {
    const isConfirmed = eventInfo.event.extendedProps.status === 'confirmed';
    const professional = eventInfo.event.extendedProps.professional;
    return (
        <div className="w-full h-full overflow-hidden text-ellipsis px-1.5 py-0.5 flex flex-col justify-center" title={`${eventInfo.event.title} (${professional})`}>
            <div className="flex items-center gap-1.5 mb-0.5">
                <div className={`w-1.5 h-1.5 rounded-full shrink-0 ${isConfirmed ? 'bg-brand-text-primary/80' : 'bg-brand-text-secondary/40'}`}></div>
                <b className="font-bold text-[10px] md:text-xs tracking-tight text-brand-text-primary">{eventInfo.timeText}</b>
            </div>
            <span className="font-semibold text-[11px] md:text-xs truncate text-brand-text-primary leading-tight">
                {eventInfo.event.title}
            </span>
            <span className="text-[9px] md:text-[10px] text-brand-text-secondary truncate mt-0.5 font-medium">
                {professional}
            </span>
        </div>
    );
}

export const Dashboard = () => {
    const [appointments, setAppointments] = useState<Appointment[]>([]);
    const [isSidebarOpen, setSidebarOpen] = useState(false);
    const [toasts, setToasts] = useState<{ id: string, message: string, type: 'success' | 'error' }[]>([]);
    const navigate = useNavigate();

    // Modals state
    const [isFormModalOpen, setFormModalOpen] = useState(false);
    const [isDetailsModalOpen, setDetailsModalOpen] = useState(false);
    const [editingId, setEditingId] = useState<string | null>(null);
    const [selectedEvent, setSelectedEvent] = useState<any>(null);

    const [formData, setFormData] = useState({ patient_name: '', patient_phone: '', datetime: '', service: 'Clínica Geral', professional: 'Clínica Geral' });
    const calendarRef = useRef<FullCalendar>(null);

    const loadData = async () => {
        try {
            const data = await fetchAppointments();
            setAppointments(data.appointments);
        } catch (error: any) {
            if (error.message.includes('401') || error.message.includes('Failed to fetch')) {
                localStorage.removeItem('token');
                navigate('/login');
            } else {
                showToast('Erro ao carregar dados', 'error');
            }
        }
    };

    useEffect(() => {
        loadData();
        const handleResize = () => {
            const isMobile = window.innerWidth < 768;
            const api = calendarRef.current?.getApi();
            if (!api) return;
            const currentView = api.view.type;
            if (isMobile && currentView !== 'listWeek') api.changeView('listWeek');
            else if (!isMobile && currentView === 'listWeek') api.changeView('dayGridMonth');
        };
        window.addEventListener('resize', handleResize);
        handleResize();
        return () => window.removeEventListener('resize', handleResize);
    }, []);

    const showToast = (message: string, type: 'success' | 'error' = 'success') => {
        const id = Math.random().toString(36).substr(2, 9);
        setToasts(prev => [...prev, { id, message, type }]);
    };

    const removeToast = (id: string) => setToasts(prev => prev.filter(t => t.id !== id));

    const todayStr = new Date().toISOString().split('T')[0];
    const todayCount = appointments.filter(a => a.datetime.startsWith(todayStr)).length;
    const confirmedCount = appointments.filter(a => a.status === 'confirmed').length;
    const confirmationRate = appointments.length ? Math.round((confirmedCount / appointments.length) * 100) : 0;

    const handleEventClick = (info: any) => {
        setSelectedEvent(info.event);
        setDetailsModalOpen(true);
    };

    const handleCreateNew = () => {
        setEditingId(null);
        setFormData({ patient_name: '', patient_phone: '', datetime: '', service: 'Clínica Geral', professional: 'Clínica Geral' });
        setFormModalOpen(true);
    };

    const handleEdit = () => {
        setDetailsModalOpen(false);
        setEditingId(selectedEvent.id);
        const props = selectedEvent.extendedProps;
        const d = selectedEvent.start;
        const localDateTime = new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
        setFormData({
            patient_name: selectedEvent.title,
            patient_phone: props.phone,
            datetime: localDateTime,
            service: props.service || 'Clínica Geral',
            professional: props.professional || 'Clínica Geral'
        });
        setFormModalOpen(true);
    };

    const handleDelete = async () => {
        if (!confirm('Excluir este agendamento?')) return;
        try {
            await deleteAppointment(selectedEvent.id);
            showToast('Agendamento excluído!', 'success');
            setDetailsModalOpen(false);
            loadData();
        } catch (e) {
            showToast('Erro ao excluir', 'error');
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            if (editingId) {
                await updateAppointment(editingId, formData);
                showToast('Agendamento atualizado!', 'success');
            } else {
                await createAppointment(formData);
                showToast('Agendamento criado!', 'success');
            }
            setFormModalOpen(false);
            loadData();
        } catch (e) {
            showToast('Erro no servidor', 'error');
        }
    };

    const events = appointments.map(apt => {
        let bgColor = '#FFFFFF'; // Default pending background (white)

        if (apt.status === 'confirmed') {
            // Faint pastels for confirmed, distinguished by professional
            if (apt.professional === 'Ortodontia') bgColor = '#DBEAFE'; // Minimalist Blue
            else if (apt.professional === 'Dra. Débora / Dr. Sidney') bgColor = '#FCE7F3'; // Minimalist Pink
            else bgColor = '#D1FAE5'; // Minimalist Green
        }

        return {
            id: apt.id,
            title: apt.patient_name,
            start: apt.datetime,
            extendedProps: { phone: apt.patient_phone, service: apt.service, professional: apt.professional, status: apt.status },
            backgroundColor: bgColor,
            textColor: '#111827', // Always dark text
            borderColor: apt.status === 'confirmed' ? 'transparent' : '#E5E7EB', // Faint border if pending
        };
    });

    return (
        <div className="flex h-screen bg-brand-bg font-inter overflow-hidden relative">
            <Sidebar isMobileOpen={isSidebarOpen} toggleSidebar={() => setSidebarOpen(!isSidebarOpen)} />

            <main className="flex-1 flex flex-col h-screen overflow-hidden">
                <header className="h-[76px] bg-white border-b border-brand-border flex items-center justify-between px-6 md:px-10 shrink-0">
                    <div className="flex items-center gap-4">
                        <button onClick={() => setSidebarOpen(true)} className="md:hidden text-2xl text-brand-text-primary focus:outline-none">☰</button>
                        <h1 className="text-2xl font-bold text-brand-text-primary tracking-tight">Schedule</h1>
                    </div>
                    <button onClick={handleCreateNew} className="btn-primary shadow-sm">+ New Event</button>
                </header>

                <div className="flex-1 overflow-y-auto p-4 md:p-10">
                    <div className="max-w-[1600px] mx-auto flex flex-col gap-8">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            {/* KPI Cards styled for minimal logic without nested borders */}
                            <div className="bg-white rounded-2xl p-6 shadow-sm border border-brand-border/50 flex flex-col justify-center">
                                <span className="text-sm font-semibold text-brand-text-secondary uppercase tracking-widest mb-2">Today's Load</span>
                                <div className="text-4xl font-bold text-brand-text-primary">{todayCount}</div>
                                <span className="text-xs text-brand-text-secondary mt-2 font-medium">{todayCount > 0 ? 'Appointments Scheduled' : 'No patients today'}</span>
                            </div>
                            <div className="bg-white rounded-2xl p-6 shadow-sm border border-brand-border/50 flex flex-col justify-center">
                                <span className="text-sm font-semibold text-brand-text-secondary uppercase tracking-widest mb-2">Active Overall</span>
                                <div className="text-4xl font-bold text-brand-text-primary">{appointments.length}</div>
                            </div>
                            <div className="bg-white rounded-2xl p-6 shadow-sm border border-brand-border/50 flex flex-col justify-center">
                                <span className="text-sm font-semibold text-brand-text-secondary uppercase tracking-widest mb-2">Confirmation Rate</span>
                                <div className="text-4xl font-bold text-brand-text-primary">{confirmationRate}%</div>
                            </div>
                        </div>

                        <div className="bg-white rounded-2xl p-6 shadow-sm border border-brand-border/50">
                            <FullCalendar
                                ref={calendarRef}
                                plugins={[dayGridPlugin, timeGridPlugin, listPlugin, interactionPlugin]}
                                initialView="dayGridMonth"
                                headerToolbar={{ left: 'prev,next today', center: 'title', right: 'dayGridMonth,timeGridWeek,timeGridDay' }}
                                locale="en"
                                height="auto"
                                events={events}
                                eventClick={handleEventClick}
                                eventContent={renderEventContent}
                                dayMaxEvents={4}
                                slotMinTime="08:00:00"
                                slotMaxTime="18:30:00"
                                allDaySlot={false}
                            />
                        </div>
                    </div>
                </div>
            </main>

            {/* Details Modal */}
            {isDetailsModalOpen && selectedEvent && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm" onClick={() => setDetailsModalOpen(false)}>
                    <div className="bg-white rounded-xl shadow-xl w-full max-w-md p-6 animate-[slideUp_0.2s_ease-out]" onClick={e => e.stopPropagation()}>
                        <div className="flex justify-between items-center mb-6">
                            <h2 className="text-xl font-semibold text-brand-text-primary">Detalhes</h2>
                            <button onClick={() => setDetailsModalOpen(false)} className="text-gray-400 hover:text-brand-text-primary text-2xl leading-none">&times;</button>
                        </div>

                        <div className="space-y-4">
                            <div>
                                <label className="text-xs font-semibold uppercase tracking-wider text-brand-text-secondary mb-1 block">Paciente</label>
                                <div className="text-lg font-bold text-brand-text-primary">{selectedEvent.title}</div>
                            </div>
                            <div>
                                <label className="text-xs font-semibold uppercase tracking-wider text-brand-text-secondary mb-1 block">Telefone</label>
                                <div className="text-brand-text-primary font-medium">{selectedEvent.extendedProps.phone}</div>
                            </div>
                            <div>
                                <label className="text-xs font-semibold uppercase tracking-wider text-brand-text-secondary mb-1 block">Data / Hora</label>
                                <div className="text-brand-text-primary font-medium">{selectedEvent.start?.toLocaleString('pt-BR')}</div>
                            </div>
                            <div>
                                <label className="text-xs font-semibold uppercase tracking-wider text-brand-text-secondary mb-1 block">Status</label>
                                <span className={`inline-block px-3 py-1 rounded-full text-xs font-bold text-white shadow-sm ${selectedEvent.extendedProps.status === 'confirmed' ? 'bg-brand-success' : 'bg-brand-text-secondary'}`}>
                                    {selectedEvent.extendedProps.status === 'confirmed' ? 'Confirmado' : 'Aguardando'}
                                </span>
                            </div>
                        </div>

                        <div className="mt-8 flex gap-3">
                            <button onClick={handleEdit} className="btn-secondary flex-1 border-[#007BFF] text-[#007BFF] hover:bg-blue-50">Editar</button>
                            <button onClick={handleDelete} className="btn-danger flex-1">Excluir</button>
                        </div>
                    </div>
                </div>
            )}

            {/* Form Modal */}
            {isFormModalOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm" onClick={() => setFormModalOpen(false)}>
                    <div className="bg-white rounded-xl shadow-xl w-full max-w-md p-6 animate-[slideUp_0.2s_ease-out]" onClick={e => e.stopPropagation()}>
                        <div className="flex justify-between items-center mb-6">
                            <h2 className="text-xl font-semibold text-brand-text-primary">{editingId ? 'Editar Agendamento' : 'Nova Consulta'}</h2>
                            <button onClick={() => setFormModalOpen(false)} className="text-gray-400 hover:text-brand-text-primary text-2xl leading-none">&times;</button>
                        </div>

                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div>
                                <label className="form-label">Nome do Paciente</label>
                                <input required className="input-field" value={formData.patient_name} onChange={e => setFormData({ ...formData, patient_name: e.target.value })} />
                            </div>
                            <div>
                                <label className="form-label">Telefone</label>
                                <input required className="input-field" placeholder="551199999999" value={formData.patient_phone} onChange={e => setFormData({ ...formData, patient_phone: e.target.value })} />
                            </div>
                            <div>
                                <label className="form-label">Data e Hora</label>
                                <input required type="datetime-local" className="input-field" value={formData.datetime} onChange={e => setFormData({ ...formData, datetime: e.target.value })} />
                            </div>
                            <div>
                                <label className="form-label">Serviço</label>
                                <select className="input-field" value={formData.service} onChange={e => setFormData({ ...formData, service: e.target.value })}>
                                    {["Odontopediatria (1ª vez)", "Odontopediatria (Retorno)", "Pacientes Especiais (1ª vez)", "Pacientes Especiais (Retorno)", "Implante", "Clínica Geral", "Ortodontia", "Fonoaudióloga miofuncional"].map(s => (
                                        <option key={s} value={s}>{s}</option>
                                    ))}
                                </select>
                            </div>
                            <div>
                                <label className="form-label">Profissional</label>
                                <select className="input-field" value={formData.professional} onChange={e => setFormData({ ...formData, professional: e.target.value })}>
                                    {["Clínica Geral", "Ortodontia", "Dra. Débora / Dr. Sidney"].map(p => (
                                        <option key={p} value={p}>{p}</option>
                                    ))}
                                </select>
                            </div>
                            <div className="pt-4">
                                <button type="submit" className="btn-primary w-full">Salvar Agendamento</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Toasts */}
            <div className="fixed bottom-6 right-6 z-[60] flex flex-col gap-3">
                {toasts.map(toast => <Toast key={toast.id} {...toast} onClose={() => removeToast(toast.id)} />)}
            </div>
        </div>
    );
};
