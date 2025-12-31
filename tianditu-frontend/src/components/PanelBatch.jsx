import React, { useState } from 'react';

export default function PanelBatch({ map }) {
  const [input, setInput] = useState('');

  const handleClick = async () => {
    if (!map) return;
    map.clearOverLays();
    if (!input.trim()) return alert('Enter IDs or addresses');

    const items = input.split(/[\n,]+/).map(s => s.trim()).filter(Boolean);
    const allIds = items.every(s => /^\d+$/.test(s));
    const payload = allIds
      ? { ids: items.map(Number) }
      : { addresses: items };

    const resp = await fetch(`${API_URL}/locations/batch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!resp.ok) return alert((await resp.json()).error);
    const data = await resp.json();
    if (!data.length) return alert('No matches');

    const bounds = new window.T.LngLatBounds();
    data.forEach(rec => {
      const [lon, lat] = JSON.parse(rec.geometry).coordinates;
      const pt = new window.T.LngLat(lon, lat);
      map.addOverLay(new window.T.Marker(pt));
      bounds.extend(pt);
    });
    map.setMapStatus({
      center: bounds.getCenter(),
      zoom: map.getBoundsZoomLevel(bounds)
    });
  };

  return (
    <div style={{ padding: 12 }}>
      <h4>Batch Plot Locations</h4>
      <textarea
        rows={5}
        style={{ width: '100%' }}
        value={input}
        onChange={e => setInput(e.target.value)}
        placeholder="IDs: 1,2,3 or addresses, one per line"
      />
      <br /><br />
      <button onClick={handleClick}>Plot All</button>
    </div>
  );
}