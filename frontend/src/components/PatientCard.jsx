import { User, Activity } from 'lucide-react'

const statusConfig = {
  CRITICAL : { color: '#EF4444', bg: 'rgba(239,68,68,0.1)',  label: 'CRITICAL', blink: true  },
  WARNING  : { color: '#F59E0B', bg: 'rgba(245,158,11,0.1)', label: 'WARNING',  blink: false },
  NORMAL   : { color: '#10B981', bg: 'rgba(16,185,129,0.1)', label: 'NORMAL',   blink: false },
}

export default function PatientCard({ patient, isSelected, onClick, status }) {
  const cfg = statusConfig[status] || statusConfig.NORMAL

  return (
    <button
      onClick={onClick}
      style={{
        background   : isSelected ? 'rgba(56,189,248,0.08)' : 'var(--navy-card)',
        borderColor  : isSelected ? 'var(--accent)' : 'var(--border)',
        borderWidth  : '1px',
        borderStyle  : 'solid',
        borderRadius : '6px',
        padding      : '14px 16px',
        width        : '100%',
        textAlign    : 'left',
        cursor       : 'pointer',
        transition   : 'all 0.15s ease',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: '34px', height: '34px', borderRadius: '50%',
            background: 'rgba(56,189,248,0.1)',
            display: 'flex', alignItems: 'center', justifyContent: 'center'
          }}>
            <User size={16} color="var(--accent)" />
          </div>
          <div>
            <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--white)' }}>
              {patient.name}
            </div>
            <div style={{ fontSize: '11px', color: 'var(--steel)', marginTop: '2px' }}>
              {patient.patient_id} · Age {patient.age}
            </div>
          </div>
        </div>

        {status && (
          <span
            className={cfg.blink ? 'blink' : ''}
            style={{
              fontSize: '9px', fontWeight: 700,
              letterSpacing: '0.08em',
              color: cfg.color,
              background: cfg.bg,
              padding: '3px 8px',
              borderRadius: '3px',
              fontFamily: 'IBM Plex Mono, monospace',
            }}
          >
            {cfg.label}
          </span>
        )}
      </div>

      <div style={{ marginTop: '10px', display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
        {patient.conditions?.map(c => (
          <span key={c} style={{
            fontSize: '10px', color: 'var(--steel)',
            background: 'rgba(203,213,225,0.06)',
            padding: '2px 7px', borderRadius: '3px',
            border: '1px solid var(--border)',
            textTransform: 'capitalize',
          }}>
            {c}
          </span>
        ))}
      </div>
    </button>
  )
}