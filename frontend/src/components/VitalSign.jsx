const paramLabel = {
  heart_rate       : { label: 'HR',    unit: 'bpm',   icon: '♥' },
  systolic_bp      : { label: 'SYS',   unit: 'mmHg',  icon: '↑' },
  diastolic_bp     : { label: 'DIA',   unit: 'mmHg',  icon: '↓' },
  spo2             : { label: 'SpO₂',  unit: '%',     icon: '○' },
  temperature      : { label: 'TEMP',  unit: '°C',    icon: '◈' },
  respiratory_rate : { label: 'RR',    unit: 'br/min',icon: '~' },
  blood_glucose    : { label: 'GLU',   unit: 'mg/dL', icon: '◇' },
}

const statusColor = {
  CRITICAL : '#EF4444',
  WARNING  : '#F59E0B',
  NORMAL   : '#10B981',
}

export default function VitalSign({ parameter, value, unit, status }) {
  const meta  = paramLabel[parameter] || { label: parameter, unit, icon: '·' }
  const color = statusColor[status] || '#10B981'
  const isHR  = parameter === 'heart_rate'

  return (
    <div style={{
      background   : 'var(--navy-card)',
      border       : `1px solid ${status === 'CRITICAL' ? 'rgba(239,68,68,0.3)' : 'var(--border)'}`,
      borderRadius : '6px',
      padding      : '14px',
      position     : 'relative',
      overflow     : 'hidden',
    }}>
      {/* top accent line */}
      <div style={{
        position: 'absolute', top: 0, left: 0, right: 0,
        height: '2px', background: color,
      }} />

      <div style={{
        fontSize: '9px', fontWeight: 700,
        letterSpacing: '0.12em', color: 'var(--steel)',
        fontFamily: 'IBM Plex Mono, monospace',
        marginBottom: '8px',
        display: 'flex', justifyContent: 'space-between'
      }}>
        <span>{meta.label}</span>
        <span style={{ opacity: 0.5 }}>{meta.icon}</span>
      </div>

      <div style={{ display: 'flex', alignItems: 'baseline', gap: '4px' }}>
        <span
          className={`font-mono ${isHR && status !== 'NORMAL' ? 'pulse' : ''}`}
          style={{
            fontSize: '28px', fontWeight: 600,
            color: color, lineHeight: 1,
          }}
        >
          {value}
        </span>
        <span style={{ fontSize: '11px', color: 'var(--steel)', fontFamily: 'IBM Plex Mono, monospace' }}>
          {meta.unit}
        </span>
      </div>

      <div style={{
        marginTop: '8px', fontSize: '9px',
        fontFamily: 'IBM Plex Mono, monospace',
        color: color, fontWeight: 600,
        letterSpacing: '0.08em',
      }}>
        {status}
      </div>
    </div>
  )
}