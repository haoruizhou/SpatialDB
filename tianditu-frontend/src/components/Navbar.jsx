import React from 'react';

/**
 * Navbar component to switch between panels
 * Props:
 *  - setPanel: function to change active panel ('single', 'batch', 'spatial')
 *  - clear: function to clear all map overlays
 */
export default function Navbar({ setPanel, clear }) {
  const modes = [
    { key: 'single', label: 'Plot Single' },
    { key: 'batch', label: 'Batch Plot' },
    { key: 'spatial', label: 'Spatial Query' }
  ];

  return (
    <div style={{ background: '#333', color: '#fff', padding: '8px', display: 'flex' }}>
      {modes.map(({ key, label }) => (
        <button
          key={key}
          onClick={() => { clear(); setPanel(key); }}
          style={{
            marginRight: '8px',
            background: '#fff',
            color: '#333',
            border: 'none',
            padding: '8px 12px',
            cursor: 'pointer'
          }}
        >
          {label}
        </button>
      ))}
    </div>
  );
}