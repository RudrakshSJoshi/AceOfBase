// components/Layout/FuturisticLayout.jsx
import React from 'react';
import Rhombus from './Rhombus';
import './FuturisticPage.css';

const FuturisticLayout = ({ children }) => {
  // Generate multiple rhombus with different properties
  const rhombusConfigs = [
    { size: 80, color: '#4fc3f7', delay: 0, duration: 15 },
    { size: 120, color: '#ff4081', delay: 3, duration: 20 },
    { size: 60, color: '#7c4dff', delay: 7, duration: 25 },
    { size: 100, color: '#00e676', delay: 5, duration: 18 },
  ];

  return (
    <div className="futuristic-container">
      {/* Background with floating rhombus */}
      <div className="background-animation">
        {rhombusConfigs.map((config, index) => (
          <Rhombus key={index} {...config} />
        ))}
      </div>
      
      {/* Main content box with blur effect */}
      <div className="content-box">
        {children}
      </div>
    </div>
  );
};

export default FuturisticLayout;