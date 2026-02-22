import { useEffect } from 'react';

export const Toast = ({ message, type, onClose }: { message: string, type: 'success' | 'error', onClose: () => void }) => {
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
