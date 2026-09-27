interface Option { value: string; label: string }
interface Props { id: string; label: string; value: string; onChange: (v: string) => void; options: Option[]; help?: string; className?: string }

export default function SelectField({ id, label, value, onChange, options, help, className = '' }: Props) {
  return (
    <div className={`grid grid-rows-subgrid row-span-3 content-start gap-y-0 ${className}`}>
      <label htmlFor={id} className="mb-1 block text-sm font-medium text-navy-700">{label}</label>
      <select id={id} value={value} onChange={(e) => onChange(e.target.value)} aria-describedby={help ? `${id}-help` : undefined}
        className="w-full rounded-lg border border-navy-300 h-12 bg-white px-3 text-navy-900 focus:border-accent-500 focus:outline-none focus:ring-2 focus:ring-accent-500/20">
        {options.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
      {help && <p id={`${id}-help`} className="mt-1 text-xs text-navy-500">{help}</p>}
    </div>
  );
}
