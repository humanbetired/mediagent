import { useEffect, useRef } from 'react'
import ReactMarkdown from 'react-markdown'

const mdComponents = {
  h1: ({ children }) => (
      <div style={{
      fontSize: '11px', fontWeight: 700, letterSpacing: '0.08em',
      color: 'var(--accent)', marginTop: '14px', marginBottom: '8px',
      fontFamily: 'IBM Plex Mono, monospace', textTransform: 'uppercase',
      borderBottom: '1px solid var(--border)', paddingBottom: '6px',
      }}>
        {children}
      </div>
  ),
  h2: ({ children }) => (
    <div style={{
      fontSize: '11px', fontWeight: 700, letterSpacing: '0.08em',
      color: 'var(--accent)', marginTop: '14px', marginBottom: '6px',
      fontFamily: 'IBM Plex Mono, monospace', textTransform: 'uppercase',
    }}>
      {children}
    </div>
  ),
  h3: ({ children }) => (
    <div style={{
      fontSize: '10px', fontWeight: 700, letterSpacing: '0.06em',
      color: 'var(--steel)', marginTop: '10px', marginBottom: '4px',
      fontFamily: 'IBM Plex Mono, monospace', textTransform: 'uppercase',
    }}>
      {children}
    </div>
  ),
  p: ({ children }) => (
    <p style={{
      fontSize: '13px', lineHeight: '1.7', color: 'var(--steel)',
      marginBottom: '8px',
    }}>
      {children}
    </p>
  ),
  strong: ({ children }) => (
    <strong style={{ color: 'var(--white)', fontWeight: 600 }}>
      {children}
    </strong>
  ),
  em: ({ children }) => (
    <em style={{ color: 'var(--accent)', fontStyle: 'normal' }}>
      {children}
    </em>
  ),
  ul: ({ children }) => (
    <ul style={{
      margin: '4px 0 10px', paddingLeft: '0', listStyle: 'none',
    }}>
      {children}
    </ul>
  ),
  ol: ({ children }) => (
    <ol style={{
      margin: '4px 0 10px', paddingLeft: '0', listStyle: 'none',
      counterReset: 'item',
    }}>
      {children}
    </ol>
  ),
  li: ({ children, ordered }) => (
    <li style={{
      fontSize: '13px', lineHeight: '1.7', color: 'var(--steel)',
      paddingLeft: '18px', position: 'relative', marginBottom: '4px',
    }}>
      <span style={{
        position: 'absolute', left: 0, top: 0,
        color: 'var(--accent)', fontFamily: 'IBM Plex Mono, monospace',
        fontSize: '12px',
      }}>
        {ordered ? '▸' : '·'}
      </span>
      {children}
    </li>
  ),
  code: ({ children }) => (
    <code style={{
      background: 'rgba(56,189,248,0.08)',
      color: 'var(--accent)',
      padding: '1px 5px', borderRadius: '3px',
      fontFamily: 'IBM Plex Mono, monospace', fontSize: '12px',
    }}>
      {children}
    </code>
  ),
  hr: () => (
    <hr style={{ border: 'none', borderTop: '1px solid var(--border)', margin: '10px 0' }} />
  ),
}

export default function StreamingAssessment({ tokens, isStreaming, ragGuidance }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [tokens])

  if (!tokens && !isStreaming) return null

  return (
    <div style={{
      background: 'var(--navy-card)',
      border: '1px solid var(--border)',
      borderRadius: '6px',
      overflow: 'hidden',
    }}>
      {/* Header */}
      <div style={{
        padding: '10px 16px',
        borderBottom: '1px solid var(--border)',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        background: 'rgba(56,189,248,0.04)',
      }}>
        <span style={{
          fontSize: '10px', fontWeight: 700,
          letterSpacing: '0.1em', color: 'var(--accent)',
          fontFamily: 'IBM Plex Mono, monospace',
        }}>
          RISK ASSESSMENT ANALYSIS
        </span>
        {isStreaming && (
          <span style={{
            fontSize: '9px', color: 'var(--normal)',
            fontFamily: 'IBM Plex Mono, monospace',
            display: 'flex', alignItems: 'center', gap: '6px',
          }}>
            <span className="pulse" style={{
              width: '6px', height: '6px', borderRadius: '50%',
              background: 'var(--normal)', display: 'inline-block'
            }} />
            LIVE
          </span>
        )}
      </div>

      {/* Content */}
      <div style={{ padding: '16px', maxHeight: '280px', overflowY: 'auto' }}>
        <pre style={{
          fontFamily: 'Inter, sans-serif',
          fontSize: '13px', lineHeight: '1.7',
          color: 'var(--steel)', whiteSpace: 'pre-wrap',
          wordBreak: 'break-word',
        }}>
          {tokens}
          {isStreaming && (
            <span style={{
              display: 'inline-block', width: '2px', height: '14px',
              background: 'var(--accent)', marginLeft: '2px',
              animation: 'blink-critical 0.8s ease-in-out infinite',
              verticalAlign: 'middle',
            }} />
          )}
        </pre>
        <div ref={bottomRef} />
      </div>

      {/* RAG Guidance */}
      {ragGuidance && (
        <>
          <div style={{ borderTop: '1px solid var(--border)', padding: '10px 16px',
            background: 'rgba(16,185,129,0.04)',
          }}>
            <span style={{
              fontSize: '10px', fontWeight: 700,
              letterSpacing: '0.1em', color: 'var(--normal)',
              fontFamily: 'IBM Plex Mono, monospace',
            }}>
              CLINICAL PROTOCOL REFERENCE
            </span>
          </div>
          <div style={{ padding: '14px 16px', maxHeight: '200px', overflowY: 'auto' }}>
            <ReactMarkdown components={mdComponents}>
              {ragGuidance}
            </ReactMarkdown>
          </div>
        </>
      )}
    </div>
  )
}