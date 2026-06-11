import { useState, useEffect, useCallback } from 'react'
import { Activity, Users, Bell, RefreshCw, Zap } from 'lucide-react'
import PatientCard from './components/PatientCard'
import VitalSign from './components/VitalSign'
import StreamingAssessment from './components/StreamingAssessment'

const API = 'http://localhost:8000'

export default function App() {
  const [patients,      setPatients]      = useState([])
  const [selected,      setSelected]      = useState(null)
  const [vitalFindings, setVitalFindings] = useState(null)
  const [overallStatus, setOverallStatus] = useState(null)
  const [tokens,        setTokens]        = useState('')
  const [isStreaming,   setIsStreaming]    = useState(false)
  const [ragGuidance,   setRagGuidance]   = useState(null)
  const [statusMap,     setStatusMap]     = useState({})
  const [alerts,        setAlerts]        = useState([])
  const [time,          setTime]          = useState(new Date())

  // Clock
  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(t)
  }, [])

  // Load patients
  useEffect(() => {
    fetch(`${API}/api/patients`)
      .then(r => r.json())
      .then(d => setPatients(d.patients))
  }, [])

  const runAnalysis = useCallback((patient) => {
    setSelected(patient)
    setVitalFindings(null)
    setOverallStatus(null)
    setTokens('')
    setRagGuidance(null)
    setIsStreaming(false)

    const es = new EventSource(`${API}/api/stream/${patient.patient_id}`)

    es.addEventListener('vital_result', e => {
      const d = JSON.parse(e.data)
      setVitalFindings(d.findings)
      setOverallStatus(d.overall_status)
      setStatusMap(prev => ({ ...prev, [patient.patient_id]: d.overall_status }))
      if (d.overall_status !== 'NORMAL') {
        setAlerts(prev => [{
          id        : Date.now(),
          patient   : patient.name,
          patient_id: patient.patient_id,
          status    : d.overall_status,
          params    : [...d.critical_params, ...d.warning_params],
          time      : new Date().toLocaleTimeString(),
        }, ...prev.slice(0, 4)])
      }
    })

    es.addEventListener('step', e => {
      const d = JSON.parse(e.data)
      if (d.agent === 'RiskAnalysis') setIsStreaming(true)
    })

    es.addEventListener('token', e => {
      const d = JSON.parse(e.data)
      setTokens(prev => prev + d.text)
    })

    es.addEventListener('rag_result', e => {
      const d = JSON.parse(e.data)
      setRagGuidance(d.answer)
    })

    es.addEventListener('done', () => {
      setIsStreaming(false)
      es.close()
    })

    es.addEventListener('error', () => {
      setIsStreaming(false)
      es.close()
    })
  }, [])

  const statusBg = {
    CRITICAL : 'rgba(239,68,68,0.12)',
    WARNING  : 'rgba(245,158,11,0.12)',
    NORMAL   : 'rgba(16,185,129,0.12)',
  }
  const statusColor = { CRITICAL: '#EF4444', WARNING: '#F59E0B', NORMAL: '#10B981' }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>

      {/* ── Top Bar ── */}
      <header style={{
        background   : 'var(--navy-mid)',
        borderBottom : '1px solid var(--border)',
        padding      : '0 24px',
        height       : '52px',
        display      : 'flex', alignItems: 'center', justifyContent: 'space-between',
        flexShrink   : 0,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Activity size={18} color="var(--accent)" />
          <span style={{
            fontFamily: 'IBM Plex Mono, monospace',
            fontSize: '13px', fontWeight: 600, color: 'var(--white)',
            letterSpacing: '0.05em',
          }}>
            MEDIAGENT
          </span>
          <span style={{
            fontSize: '10px', color: 'var(--steel)',
            background: 'rgba(203,213,225,0.06)',
            padding: '2px 8px', borderRadius: '3px',
            border: '1px solid var(--border)',
            fontFamily: 'IBM Plex Mono, monospace',
          }}>
            ICU MONITORING SYSTEM
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          {alerts.length > 0 && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Bell size={14} color="#F59E0B" />
              <span style={{ fontSize: '11px', color: '#F59E0B', fontFamily: 'IBM Plex Mono, monospace' }}>
                {alerts.length} ALERT{alerts.length > 1 ? 'S' : ''}
              </span>
            </div>
          )}
          <span style={{
            fontFamily: 'IBM Plex Mono, monospace',
            fontSize: '12px', color: 'var(--steel)',
          }}>
            {time.toLocaleTimeString('en-GB')}
          </span>
        </div>
      </header>

      {/* ── Body ── */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>

        {/* ── Sidebar ── */}
        <aside style={{
          width: '240px', flexShrink: 0,
          background: 'var(--navy-mid)',
          borderRight: '1px solid var(--border)',
          display: 'flex', flexDirection: 'column',
          overflow: 'hidden',
        }}>
          <div style={{
            padding: '14px 16px 10px',
            borderBottom: '1px solid var(--border)',
            display: 'flex', alignItems: 'center', gap: '8px',
          }}>
            <Users size={13} color="var(--steel)" />
            <span style={{
              fontSize: '10px', fontWeight: 700,
              letterSpacing: '0.1em', color: 'var(--steel)',
              fontFamily: 'IBM Plex Mono, monospace',
            }}>
              PATIENTS ({patients.length})
            </span>
          </div>

          <div style={{ padding: '10px 12px', display: 'flex', flexDirection: 'column', gap: '8px', overflowY: 'auto' }}>
            {patients.map(p => (
              <PatientCard
                key={p.patient_id}
                patient={p}
                isSelected={selected?.patient_id === p.patient_id}
                status={statusMap[p.patient_id]}
                onClick={() => runAnalysis(p)}
              />
            ))}
          </div>

          {/* Alert Log */}
          {alerts.length > 0 && (
            <div style={{ borderTop: '1px solid var(--border)', marginTop: 'auto' }}>
              <div style={{
                padding: '10px 16px 6px',
                fontSize: '10px', fontWeight: 700,
                letterSpacing: '0.1em', color: '#F59E0B',
                fontFamily: 'IBM Plex Mono, monospace',
              }}>
                RECENT ALERTS
              </div>
              <div style={{ padding: '0 12px 12px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {alerts.slice(0, 3).map(a => (
                  <div key={a.id} style={{
                    background: statusBg[a.status],
                    border: `1px solid ${statusColor[a.status]}30`,
                    borderRadius: '4px', padding: '8px 10px',
                  }}>
                    <div style={{ fontSize: '10px', fontWeight: 600, color: statusColor[a.status] }}>
                      {a.status}
                    </div>
                    <div style={{ fontSize: '10px', color: 'var(--steel)', marginTop: '2px' }}>
                      {a.patient}
                    </div>
                    <div style={{
                      fontSize: '9px', color: 'var(--steel)', opacity: 0.6,
                      fontFamily: 'IBM Plex Mono, monospace', marginTop: '2px'
                    }}>
                      {a.time}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </aside>

        {/* ── Main Panel ── */}
        <main style={{ flex: 1, overflow: 'auto', padding: '20px 24px' }}>
          {!selected ? (
            <div style={{
              height: '100%', display: 'flex',
              flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
              gap: '12px',
            }}>
              <Activity size={40} color="var(--border)" />
              <p style={{
                fontFamily: 'IBM Plex Mono, monospace',
                fontSize: '13px', color: 'var(--steel)', letterSpacing: '0.05em'
              }}>
                SELECT A PATIENT TO BEGIN MONITORING
              </p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>

              {/* Patient Header */}
              <div style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center'
              }}>
                <div>
                  <h1 style={{ fontSize: '18px', fontWeight: 600, color: 'var(--white)' }}>
                    {selected.name}
                  </h1>
                  <p style={{
                    fontSize: '12px', color: 'var(--steel)', marginTop: '3px',
                    fontFamily: 'IBM Plex Mono, monospace',
                  }}>
                    {selected.patient_id} · Age {selected.age} · {selected.conditions?.join(', ')}
                  </p>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  {overallStatus && (
                    <div style={{
                      background: statusBg[overallStatus],
                      border: `1px solid ${statusColor[overallStatus]}40`,
                      borderRadius: '5px', padding: '8px 16px',
                      display: 'flex', alignItems: 'center', gap: '8px',
                    }}>
                      {overallStatus === 'CRITICAL' && (
                        <Zap size={14} color={statusColor[overallStatus]} className="blink" />
                      )}
                      <span style={{
                        fontFamily: 'IBM Plex Mono, monospace',
                        fontSize: '13px', fontWeight: 700,
                        color: statusColor[overallStatus],
                        letterSpacing: '0.08em',
                      }}>
                        {overallStatus}
                      </span>
                    </div>
                  )}
                  <button
                    onClick={() => runAnalysis(selected)}
                    style={{
                      background: 'rgba(56,189,248,0.08)',
                      border: '1px solid rgba(56,189,248,0.3)',
                      borderRadius: '5px', padding: '8px 14px',
                      color: 'var(--accent)', cursor: 'pointer',
                      display: 'flex', alignItems: 'center', gap: '6px',
                      fontSize: '12px', fontWeight: 500,
                    }}
                  >
                    <RefreshCw size={13} />
                    Re-analyze
                  </button>
                </div>
              </div>

              {/* Vital Signs Grid */}
              {vitalFindings && (
                <div>
                  <div style={{
                    fontSize: '10px', fontWeight: 700,
                    letterSpacing: '0.1em', color: 'var(--steel)',
                    fontFamily: 'IBM Plex Mono, monospace',
                    marginBottom: '12px',
                  }}>
                    VITAL SIGNS MONITOR
                  </div>
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fill, minmax(130px, 1fr))',
                    gap: '10px',
                  }}>
                    {vitalFindings.map(f => (
                      <VitalSign
                        key={f.parameter}
                        parameter={f.parameter}
                        value={f.value}
                        unit={f.unit}
                        status={f.status}
                      />
                    ))}
                  </div>
                </div>
              )}

              {/* Streaming Assessment */}
              <StreamingAssessment
                tokens={tokens}
                isStreaming={isStreaming}
                ragGuidance={ragGuidance}
              />

            </div>
          )}
        </main>
      </div>
    </div>
  )
}