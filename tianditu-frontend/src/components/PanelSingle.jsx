import React, { useState } from 'react';

export default function PanelSingle({ map }) {
  const [locId, setLocId] = useState('');
  const [address, setAddress] = useState('');

  const handleSubmit = async e => {
    e.preventDefault();
    if (!map) return;
    map.clearOverLays();

    let url = '';
    if (locId) {
      url = `${API_URL}/locations/${locId}`;
    } else if (address) {
      url = `${API_URL}/locations/by_address?address=${encodeURIComponent(address)}`;
    } else {
      return alert('Enter an ID or address');
    }

    const resp = await fetch(url);
    if (!resp.ok) return alert((await resp.json()).error);
    const data = await resp.json();
    const [lon, lat] = JSON.parse(data.geometry).coordinates;
    map.centerAndZoom(new window.T.LngLat(lon, lat), 15);
    map.addOverLay(new window.T.Marker(new window.T.LngLat(lon, lat)));
  };

  return (
    <form onSubmit={handleSubmit} style={{ padding: 12 }}>
      <h4>Plot Single Location</h4>
      <label>ID:</label><br />
      <input
        value={locId}
        onChange={e => setLocId(e.target.value)}
        placeholder="e.g. 42"
      /><br /><br />
      <label>OR Address:</label><br />
      <input
        value={address}
        onChange={e => setAddress(e.target.value)}
        placeholder="e.g. 123 Main St"
      /><br /><br />
      <button type="submit">Show</button>
    </form>
  );
}