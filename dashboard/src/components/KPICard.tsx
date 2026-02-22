export const KPICard = ({ label, value, subtext, subtextColor = 'text-brand-success' }: { label: string, value: string | number, subtext?: string, subtextColor?: string }) => (
    <div className="card flex flex-col justify-center">
        <div className="text-sm font-medium text-brand-text-secondary uppercase tracking-wider mb-2">{label}</div>
        <div className="text-3xl font-bold text-brand-text-primary">{value}</div>
        {subtext && <div className={`text-xs mt-2 font-medium ${subtextColor}`}>{subtext}</div>}
    </div>
);
