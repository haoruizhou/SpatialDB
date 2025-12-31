import React, { useState } from 'react';

export default function PanelSpatial({ map }) {
  const [centerId, setCenterId] = useState('');
  const [centerAddr, setCenterAddr] = useState('');
  const [radius, setRadius] = useState('3');

  const handleSubmit = async e => {
    e.preventDefault();
    if (!map) return;
    map.clearOverLays();

    if ((!centerId && !centerAddr) || !radius) {
      return alert('Specify center (ID or address) and radius');
    }
    const payload = { radius_km: parseFloat(radius) };
    if (centerId) payload.center_id = parseInt(centerId);
    else payload.center_addr = centerAddr;

    const resp = await fetch(`${API_URL}/competitors/within_radius`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!resp.ok) return alert((await resp.json()).error);
    const data = await resp.json();
    if (!data.length) return alert('No competitors found');

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
    <form onSubmit={handleSubmit} style={{ padding: 12 }}>
      <h4>Find Competitors Within Radius</h4>
      <label>Center ID:</label><br />
      <input
        value={centerId}
        onChange={e => setCenterId(e.target.value)}
        placeholder="e.g. 10"
      /><br /><br />
      <label>OR Center Address:</label><br />
      <input
        value={centerAddr}
        onChange={e => setCenterAddr(e.target.value)}
        placeholder="e.g. 200 Nanjing Rd"
      /><br /><br />
      <label>Radius (km):</label><br />
      <input
        value={radius}
        onChange={e => setRadius(e.target.value)}
        placeholder="e.g. 3"
      /><br /><br />
      <button type="submit">Find</button>
    </form>
);
}