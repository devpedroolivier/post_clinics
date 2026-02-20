import './style.css';
import { fetchAppointments, createAppointment, updateAppointment, deleteAppointment } from './api';
import { Calendar } from '@fullcalendar/core';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import listPlugin from '@fullcalendar/list';
import interactionPlugin from '@fullcalendar/interaction';

let currentEditingId: string | null = null;

const app = document.querySelector<HTMLDivElement>('#app')!;

// --- 1. HTML Structure (Sidebar + Main) ---
app.innerHTML = `
  <div id="sidebarOverlay" class="sidebar-overlay"></div>
  <aside class="sidebar">
    <div class="brand">POST Clinics</div>
    <ul class="nav-menu">
      <li class="nav-item active">
        <span>📅</span> Calendário
      </li>
      <li class="nav-item">
        <span>👥</span> Pacientes
      </li>
      <li class="nav-item">
        <span>⚙️</span> Configurações
      </li>
    </ul>
  </aside>

  <main class="main-content">
    <header class="header">
      <div style="display: flex; align-items: center;">
          <button id="btnMenu" style="display: none;">☰</button>
          <div class="page-title">Visão Geral</div>
      </div>
      <div class="header-actions">
        <!-- New Search Bar could go here -->
         <button id="btnNewAppointment" class="btn-primary">+ Nova Consulta</button>
      </div>
    </header>

    <div class="scrollable-area">
      <div class="dashboard-grid">
        <!-- KPI Row -->
        <div class="kpi-row">
            <div class="kpi-card">
                <div class="kpi-label">Agendamentos Hoje</div>
                <div class="kpi-value" id="kpi-today">-</div>
                <div class="kpi-sub" id="kpi-today-sub">Aguardando...</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Total Ativos</div>
                <div class="kpi-value" id="kpi-total">-</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Taxa de Confirmação</div>
                <div class="kpi-value" id="kpi-rate">0%</div>
            </div>
        </div>

        <!-- Calendar -->
        <div class="calendar-container">
            <div id="calendar"></div>
        </div>
      </div>
    </div>
  </main>

  <!-- Modals -->
  <div id="appointmentModal" class="modal">
    <div class="modal-content">
      <div class="modal-header">
        <h2>Nova Consulta</h2>
        <span class="close-btn">&times;</span>
      </div>
      <form id="appointmentForm">
        <div class="form-group">
          <label>Nome do Paciente</label>
          <input type="text" id="patientName" required>
        </div>
        <div class="form-group">
          <label>Telefone</label>
          <input type="text" id="patientPhone" placeholder="5511..." required>
        </div>
        <div class="form-group">
          <label>Data e Hora</label>
          <input type="datetime-local" id="appointmentDate" required>
        </div>
        <div class="form-group">
          <label>Serviço</label>
          <select id="service">
             <option value="Clínica Geral">Clínica Geral</option>
             <option value="Odontopediatria (1ª vez)">Odontopediatria (1ª vez)</option>
             <option value="Odontopediatria (Retorno)">Odontopediatria (Retorno)</option>
             <option value="Pacientes Especiais (1ª vez)">Pacientes Especiais (1ª vez)</option>
             <option value="Implante">Implante</option>
             <option value="Ortodontia">Ortodontia</option>
             <option value="Fonoaudióloga miofuncional">Fonoaudióloga miofuncional</option>
             <option value="Sedação endovenosa">Sedação endovenosa</option>
          </select>
        </div>
        <button type="submit" class="btn-primary" style="margin-top: 20px;">Confirmar Agendamento</button>
      </form>
    </div>
  </div>

  <div id="eventDetailsModal" class="modal">
    <div class="modal-content">
      <div class="modal-header">
        <h2 id="detailsTitle">Detalhes</h2>
        <span class="close-btn" id="closeDetails">&times;</span>
      </div>
      <div id="detailsBody">
        <!-- Details injected here -->
      </div>
    </div>
  </div>

  <!-- Toasts Container -->
  <div id="toastContainer" class="toast-container"></div>
`;

// --- 2. Sidebar Logic ---
const btnMenu = document.getElementById('btnMenu')!;
const sidebar = document.querySelector('.sidebar')!;
const overlay = document.getElementById('sidebarOverlay')!;

function toggleSidebar() {
  sidebar.classList.toggle('show');
  overlay.classList.toggle('show');
}

btnMenu.addEventListener('click', toggleSidebar);
overlay.addEventListener('click', toggleSidebar);

// Close sidebar on menu click (mobile ux)
document.querySelectorAll('.nav-item').forEach(item => {
  item.addEventListener('click', () => {
    if (window.innerWidth <= 768) toggleSidebar();
  });
});

// --- 3. Toast System ---
function showToast(message: string, type: 'success' | 'error' = 'success') {
  const container = document.getElementById('toastContainer')!;
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${message}</span>`;

  // Auto remove
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 3000);

  container.appendChild(toast);
}

// --- 3. KPI Logic ---
function updateKPIs(appointments: any[]) {
  // Total
  document.getElementById('kpi-total')!.textContent = appointments.length.toString();

  // Confirmados Rate
  const confirmed = appointments.filter(a => a.status === 'confirmed').length;
  const rate = appointments.length > 0 ? Math.round((confirmed / appointments.length) * 100) : 0;
  document.getElementById('kpi-rate')!.textContent = `${rate}%`;

  // Today
  const today = new Date().toISOString().split('T')[0];
  const todayCount = appointments.filter(a => a.datetime.startsWith(today)).length;
  document.getElementById('kpi-today')!.textContent = todayCount.toString();
  document.getElementById('kpi-today-sub')!.textContent = todayCount > 0 ? 'Agendados para hoje' : 'Nada por hoje';
}


// --- 4. Calendar Logic ---
const calendarEl = document.getElementById('calendar')!;
const calendar = new Calendar(calendarEl, {
  plugins: [dayGridPlugin, timeGridPlugin, listPlugin, interactionPlugin],
  initialView: window.innerWidth < 768 ? 'listWeek' : 'dayGridMonth',
  headerToolbar: {
    left: 'prev,next today',
    center: 'title',
    right: 'dayGridMonth,timeGridWeek'
  },
  locale: 'pt-br',
  height: '100%',
  events: async (_info, successCallback, failureCallback) => {
    try {
      const data = await fetchAppointments();
      updateKPIs(data.appointments); // Update KPIs when data loads

      const events = data.appointments.map((apt: any) => ({
        id: apt.id,
        title: apt.patient_name,
        start: apt.datetime,
        extendedProps: {
          phone: apt.patient_phone,
          service: 'Consulta', // API doesn't send service yet
          status: apt.status
        },
        color: apt.status === 'confirmed' ? '#28A745' : '#666666'
      }));
      successCallback(events);
    } catch (error) {
      showToast('Erro ao carregar dados', 'error');
      failureCallback(error as Error);
    }
  },
  eventClick: (info) => {
    // Show Details Modal
    const props = info.event.extendedProps;
    const detailsBody = document.getElementById('detailsBody')!;
    const date = info.event.start?.toLocaleString();

    detailsBody.innerHTML = `
        <div class="form-group">
            <label>Paciente</label>
            <div style="font-size: 1.1rem; font-weight: bold;">${info.event.title}</div>
        </div>
        <div class="form-group">
            <label>Telefone</label>
            <div>${props.phone}</div>
        </div>
        <div class="form-group">
            <label>Data/Hora</label>
            <div>${date}</div>
        </div>
        <div class="form-group">
            <label>Status</label>
            <div><span class="status ${props.status}" style="padding: 4px 8px; border: 1px solid black; border-radius: 4px;">${props.status}</span></div>
        </div>
        
        <div style="margin-top: 20px; display: flex; gap: 10px;">
            <button id="btnEdit" class="btn-primary" style="background-color: #007BFF;">✏️ Editar</button>
            <button id="btnDelete" class="btn-primary" style="background-color: #DC3545;">🗑️ Excluir</button>
        </div>
      `;

    const modal = document.getElementById('eventDetailsModal')!;
    modal.style.display = 'block';

    // Handle Delete
    document.getElementById('btnDelete')!.onclick = async () => {
      if (confirm('Tem certeza que deseja excluir este agendamento?')) {
        try {
          await deleteAppointment(info.event.id);
          showToast('Agendamento excluído!', 'success');
          modal.style.display = 'none';
          calendar.refetchEvents();
        } catch (e) {
          showToast('Erro ao excluir.', 'error');
        }
      }
    };

    // Handle Edit
    document.getElementById('btnEdit')!.onclick = () => {
      modal.style.display = 'none'; // Close details

      // Open form in Edit Mode
      currentEditingId = info.event.id;

      // Pre-fill form
      const nameInput = document.getElementById('patientName') as HTMLInputElement;
      const phoneInput = document.getElementById('patientPhone') as HTMLInputElement;
      const dateInput = document.getElementById('appointmentDate') as HTMLInputElement;
      const serviceInput = document.getElementById('service') as HTMLSelectElement;
      const modalTitle = document.querySelector('#appointmentModal h2')!;

      nameInput.value = info.event.title;
      phoneInput.value = props.phone;

      // Format date for datetime-local input (YYYY-MM-DDTHH:MM)
      // Adjust for timezone offset
      const d = info.event.start!;
      d.setMinutes(d.getMinutes() - d.getTimezoneOffset());
      dateInput.value = d.toISOString().slice(0, 16);

      serviceInput.value = props.service || 'Clínica Geral';

      modalTitle.textContent = 'Editar Agendamento';
      document.getElementById('appointmentModal')!.style.display = 'block';
    };
  }
});

// --- 4.5 Resize Listener ---
window.addEventListener('resize', () => {
  const isMobile = window.innerWidth < 768;
  const currentView = calendar.view.type;

  if (isMobile && currentView !== 'listWeek') {
    calendar.changeView('listWeek');
  } else if (!isMobile && currentView === 'listWeek') {
    calendar.changeView('dayGridMonth');
  }
});

calendar.render();

// --- 5. Modal & Form Handling ---
const modal = document.getElementById("appointmentModal")!;
const detailsModal = document.getElementById("eventDetailsModal")!;
const btn = document.getElementById("btnNewAppointment")!;
const closeBtns = document.querySelectorAll(".close-btn");

const closeModal = () => {
  modal.style.display = "none";
  detailsModal.style.display = "none";

  // Reset state
  currentEditingId = null;
  (document.getElementById("appointmentForm") as HTMLFormElement).reset();
  const modalTitle = document.querySelector('#appointmentModal h2')!;
  if (modalTitle) modalTitle.textContent = 'Nova Consulta';
};

btn.onclick = () => {
  currentEditingId = null;
  const modalTitle = document.querySelector('#appointmentModal h2')!;
  if (modalTitle) modalTitle.textContent = 'Nova Consulta';
  (document.getElementById("appointmentForm") as HTMLFormElement).reset();
  modal.style.display = "block";
};

closeBtns.forEach((btn: any) => {
  btn.onclick = closeModal;
});

window.onclick = (event) => {
  if (event.target == modal || event.target == detailsModal) closeModal();
}

const form = document.getElementById("appointmentForm") as HTMLFormElement;
form.onsubmit = async (e) => {
  e.preventDefault();

  const nameInput = document.getElementById('patientName') as HTMLInputElement;
  const phoneInput = document.getElementById('patientPhone') as HTMLInputElement;
  const dateInput = document.getElementById('appointmentDate') as HTMLInputElement;
  const serviceInput = document.getElementById('service') as HTMLSelectElement;

  const payload = {
    patient_name: nameInput.value,
    patient_phone: phoneInput.value,
    datetime: dateInput.value,
    service: serviceInput.value
  };

  try {
    if (currentEditingId) {
      // UPDATE MODE
      await updateAppointment(currentEditingId, payload);
      showToast('Agendamento atualizado!', 'success');
    } else {
      // CREATE MODE
      await createAppointment(payload);
      showToast('Agendamento criado!', 'success');
    }

    closeModal();
    calendar.refetchEvents();

  } catch (error) {
    console.error(error);
    showToast('Erro de conexão com o servidor.', 'error');
  }
};
