interface StatCardProps {
  label: string;
  value: string;
  unit?: string;
  hint?: string;
  tone?: 'blue' | 'orange' | 'green' | 'neutral';
}

export function StatCard({ label, value, unit, hint, tone = 'neutral' }: StatCardProps) {
  return (
    <article className={`stat-card stat-card--${tone}`}>
      <p className="stat-card__label">{label}</p>
      <p className="stat-card__value">
        {value}
        {unit ? <span className="stat-card__unit">{unit}</span> : null}
      </p>
      {hint ? <p className="stat-card__hint">{hint}</p> : null}
    </article>
  );
}
