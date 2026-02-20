import React, { useState, useEffect, useRef } from 'react';
import { createRoot } from 'react-dom/client';
import { HashRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import listPlugin from '@fullcalendar/list';
import interactionPlugin from '@fullcalendar/interaction';
import { Lock } from 'lucide-react';

import { fetchAppointments, createAppointment, updateAppointment, deleteAppointment, loginCall } from './api';
import './style.css';

// --- Types ---
type Appointment = {
  id: string;
  patient_name: string;
  patient_phone: string;
  datetime: string;
  service: string;
  status: string;
};

// --- Login Screen ---
const Login = () => {
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
      if (data.token) {
        localStorage.setItem('token', data.token);
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

// --- Dashboard Components ---
const Sidebar = ({ isMobileOpen, toggleSidebar }: { isMobileOpen: boolean, toggleSidebar: () => void }) => {
  const navigate = useNavigate();
  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <>
      <div
        className={`fixed inset-0 bg-black/50 z-40 md:hidden transition-opacity ${isMobileOpen ? 'opacity-100 block' : 'opacity-0 hidden'}`}
        onClick={toggleSidebar}
      />
      <aside className={`fixed md:sticky top-0 left-0 h-screen w-[260px] bg-brand-sidebar border-r border-brand-border flex flex-col p-8 z-50 transition-transform ${isMobileOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}`}>
        <div className="text-2xl font-bold tracking-tight text-brand-text-primary mb-8">POST Clinics</div>
        <ul className="flex flex-col gap-2 flex-1">
          {[{ icon: '📅', label: 'Calendário', active: true }, { icon: '👥', label: 'Pacientes' }, { icon: '⚙️', label: 'Configurações' }].map((item) => (
            <li
              key={item.label}
              className={`flex items-center gap-3 px-4 py-3 rounded-xl cursor-pointer font-medium transition-all ${item.active ? 'bg-white text-brand-text-primary shadow-sm border border-brand-border' : 'text-brand-text-secondary hover:bg-white hover:text-brand-text-primary hover:shadow-sm'}`}
            >
              <span>{item.icon}</span> {item.label}
            </li>
          ))}
        </ul>
        <div className="mt-auto">
          <button onClick={handleLogout} className="flex items-center gap-3 px-4 py-3 w-full rounded-xl cursor-pointer font-medium text-brand-danger hover:bg-red-50 hover:shadow-sm transition-all border border-transparent hover:border-red-100">
            <span>🚪</span> Sair
          </button>
        </div>
      </aside>
    </>
  );
};

const KPICard = ({ label, value, subtext, subtextColor = 'text-brand-success' }: { label: string, value: string | number, subtext?: string, subtextColor?: string }) => (
  <div className="card flex flex-col justify-center">
    <div className="text-sm font-medium text-brand-text-secondary uppercase tracking-wider mb-2">{label}</div>
    <div className="text-3xl font-bold text-brand-text-primary">{value}</div>
    {subtext && <div className={`text-xs mt-2 font-medium ${subtextColor}`}>{subtext}</div>}
  </div>
);

const Toast = ({ message, type, onClose }: { message: string, type: 'success' | 'error', onClose: () => void }) => {
  useEffect(() => {
    const timer = setTimeout(onClose, 3000);
    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div className={`toast-enter flex items-center justify-between min-w-[250px] p-4 rounded-xl shadow-md text-white ${type === 'success' ? 'bg-brand-success' : 'bg-brand-danger'}`}>
      <span className="font-semibold text-sm">{message}</span>
      <button onClick={onClose} className="opacity-80 hover:opacity-100 ml-4">&times;</button>
    </div>
  );
};

// --- Dashboard View App ---
const Dashboard = () => {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [isSidebarOpen, setSidebarOpen] = useState(false);
  const [toasts, setToasts] = useState<{ id: string, message: string, type: 'success' | 'error' }[]>([]);
  const navigate = useNavigate();

  // Modals state
  const [isFormModalOpen, setFormModalOpen] = useState(false);
  const [isDetailsModalOpen, setDetailsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [selectedEvent, setSelectedEvent] = useState<any>(null);

  const [formData, setFormData] = useState({ patient_name: '', patient_phone: '', datetime: '', service: 'Clínica Geral' });
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

  // --- KPI ---
  const todayStr = new Date().toISOString().split('T')[0];
  const todayCount = appointments.filter(a => a.datetime.startsWith(todayStr)).length;
  const confirmedCount = appointments.filter(a => a.status === 'confirmed').length;
  const confirmationRate = appointments.length ? Math.round((confirmedCount / appointments.length) * 100) : 0;

  // --- Handlers ---
  const handleEventClick = (info: any) => {
    setSelectedEvent(info.event);
    setDetailsModalOpen(true);
  };

  const handleCreateNew = () => {
    setEditingId(null);
    setFormData({ patient_name: '', patient_phone: '', datetime: '', service: 'Clínica Geral' });
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
      service: props.service || 'Clínica Geral'
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

  const events = appointments.map(apt => ({
    id: apt.id,
    title: apt.patient_name,
    start: apt.datetime,
    extendedProps: { phone: apt.patient_phone, service: apt.service, status: apt.status },
    backgroundColor: apt.status === 'confirmed' ? '#28A745' : '#666666',
  }));

  return (
    <div className="flex h-screen bg-brand-bg font-inter overflow-hidden relative">
      <Sidebar isMobileOpen={isSidebarOpen} toggleSidebar={() => setSidebarOpen(!isSidebarOpen)} />

      <main className="flex-1 flex flex-col h-screen overflow-hidden">
        <header className="h-[70px] bg-white border-b border-brand-border flex items-center justify-between px-8 shrink-0">
          <div className="flex items-center gap-4">
            <button onClick={() => setSidebarOpen(true)} className="md:hidden text-2xl text-brand-text-primary focus:outline-none">☰</button>
            <h1 className="text-2xl font-semibold text-brand-text-primary tracking-tight">Visão Geral</h1>
          </div>
          <button onClick={handleCreateNew} className="btn-primary shadow-sm">+ Nova Consulta</button>
        </header>

        <div className="flex-1 overflow-y-auto p-4 md:p-8">
          <div className="max-w-7xl mx-auto flex flex-col gap-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <KPICard label="Agendamentos Hoje" value={todayCount} subtext={todayCount > 0 ? 'Agendados para hoje' : 'Nada por hoje'} subtextColor={todayCount > 0 ? "text-brand-success" : "text-brand-text-secondary"} />
              <KPICard label="Total Ativos" value={appointments.length} />
              <KPICard label="Taxa de Confirmação" value={`${confirmationRate}%`} />
            </div>

            <div className="card p-4 md:p-6">
              <FullCalendar
                ref={calendarRef}
                plugins={[dayGridPlugin, timeGridPlugin, listPlugin, interactionPlugin]}
                initialView="dayGridMonth"
                headerToolbar={{ left: 'prev,next today', center: 'title', right: 'dayGridMonth,timeGridWeek' }}
                locale="pt-br"
                height="auto"
                events={events}
                eventClick={handleEventClick}
                eventContent={renderEventContent}
                dayMaxEvents={3}
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
                  {["Clínica Geral", "Odontopediatria (1ª vez)", "Odontopediatria (Retorno)", "Pacientes Especiais (1ª vez)", "Implante", "Ortodontia", "Fonoaudióloga miofuncional", "Sedação endovenosa"].map(s => (
                    <option key={s} value={s}>{s}</option>
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

// Custom Event Render for better UI
function renderEventContent(eventInfo: any) {
  const isConfirmed = eventInfo.event.extendedProps.status === 'confirmed';
  return (
    <div className={`w-full overflow-hidden text-ellipsis whitespace-nowrap px-1`} title={eventInfo.event.title}>
      <div className="flex items-center gap-1.5">
        <div className={`w-2 h-2 rounded-full shrink-0 ${isConfirmed ? 'bg-white/80' : 'bg-white/50'}`}></div>
        <b className="font-semibold text-[10px] md:text-xs tracking-tight">{eventInfo.timeText}</b>
        <span className="font-medium text-[10px] md:text-xs truncate">{eventInfo.event.title}</span>
      </div>
    </div>
  );
}

// --- Router ---
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const token = localStorage.getItem('token');
  if (!token) return <Navigate to="/login" replace />;
  return <>{children}</>;
};

const RootRouter = () => (
  <HashRouter>
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={
        <ProtectedRoute>
          <Dashboard />
        </ProtectedRoute>
      } />
    </Routes>
  </HashRouter>
);

const container = document.getElementById('app');
if (container) {
  const root = createRoot(container);
  root.render(<RootRouter />);
}
