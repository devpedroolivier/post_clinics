import { useNavigate } from 'react-router-dom';

export const Sidebar = ({ isMobileOpen, toggleSidebar }: { isMobileOpen: boolean, toggleSidebar: () => void }) => {
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
