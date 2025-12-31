import React, { useEffect, useRef, useState } from 'react';
import Navbar from './components/Navbar';
import PanelSingle from './components/PanelSingle';
import PanelBatch from './components/PanelBatch';
import PanelSpatial from './components/PanelSpatial';

let Tianditu_KEY = import.meta.env.VITE_TIANDITU_KEY;
const TIANDITU_KEY = Tianditu_KEY
    ? Tianditu_KEY
    : 'your_tianditu_key_here';

const TMapLoader = () => {
  return new Promise((resolve) => {
    if (window.T && window.T.Map) return resolve();
    const script = document.createElement('script');
    script.src = `http://api.tianditu.gov.cn/api?v=4.0&tk=${TIANDITU_KEY}`;
    script.onload = resolve;
    document.body.appendChild(script);
  });
};

export default function App() {
  const mapRef = useRef(null);
  const [panel, setPanel] = useState('single');

  useEffect(() => {
    TMapLoader().then(() => {
      const map = new window.T.Map('mapDiv');
      map.centerAndZoom(new window.T.LngLat(116.397428, 39.90923), 11);
      mapRef.current = map;
    });
  }, []);

  const clearOverlays = () => mapRef.current?.clearOverLays();

  return (
    <>
      <Navbar setPanel={setPanel} clear={clearOverlays} />
      <div style={{ display: 'flex', height: 'calc(100vh - 40px)' }}>
        {panel === 'single' && <PanelSingle map={mapRef.current} />}
        {panel === 'batch' && <PanelBatch map={mapRef.current} />}
        {panel === 'spatial' && <PanelSpatial map={mapRef.current} />}
        <div id="mapDiv" style={{ flex: 1 }}></div>
      </div>
    </>
  );
}