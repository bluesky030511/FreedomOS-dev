import dynamic from 'next/dynamic';
import React, { useEffect, useState } from 'react';

// Dynamically import MapContainer, TileLayer, Marker components with no SSR
const MapContainer = dynamic(() => import('react-leaflet').then(mod => mod.MapContainer), { ssr: false });
const TileLayer = dynamic(() => import('react-leaflet').then(mod => mod.TileLayer), { ssr: false });
const Marker = dynamic(() => import('react-leaflet').then(mod => mod.Marker), { ssr: false });

// Define the type for the component props
interface RobotMapProps {
  position: [number, number]; // Array with latitude and longitude
}

const RobotMap: React.FC<RobotMapProps> = ({ position }) => {
  const [L, setL] = useState<typeof import('leaflet') | null>(null);

  useEffect(() => {
    // Import Leaflet only on the client side
    if (typeof window !== 'undefined') {
      import('leaflet').then((leaflet) => {
        setL(leaflet);
        require('leaflet/dist/leaflet.css');
      });
    }
  }, []);

  if (!L) {
    // Render nothing or a loading indicator while Leaflet is not yet loaded
    return null;
  }

  // Create a custom blue triangle icon using the imported Leaflet
  const blueTriangleIcon = L.divIcon({
    className: 'custom-triangle-icon',
    html: `
      <div style="width: 0; height: 0; border-left: 10px solid transparent; border-right: 10px solid transparent; border-bottom: 20px solid blue; position: relative;"></div>
    `,
    iconSize: [20, 20],
    iconAnchor: [10, 20]  // Adjust to position the triangle correctly
  });

  return (
    <>
      <MapContainer center={position} zoom={13} style={{ height: "600px", width: "100%" }}>
        <TileLayer
          url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        <Marker position={position} icon={blueTriangleIcon} />
      </MapContainer>
      <style jsx global>{`
        .custom-triangle-icon {
          display: flex;
          justify-content: center;
          align-items: center;
        }
      `}</style>
    </>
  );
};

export default RobotMap;