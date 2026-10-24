import type { ReactNode } from 'react';

interface ChartPanelProps {
  title: string;
  kicker?: string;
  description?: string;
  actions?: ReactNode;
  children: ReactNode;
}

export function ChartPanel({ title, kicker, description, actions, children }: ChartPanelProps) {
  return (
    <section className="chart-panel">
      <header className="chart-panel__header">
        <div>
          {kicker ? <p className="kicker">{kicker}</p> : null}
          <h2>{title}</h2>
          {description ? <p className="chart-panel__description">{description}</p> : null}
        </div>
        {actions ? <div className="chart-panel__actions">{actions}</div> : null}
      </header>
      {children}
    </section>
  );
}
