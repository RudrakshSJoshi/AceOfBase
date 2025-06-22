// components/Layout/Rhombus.jsx
import React, { useEffect, useRef } from 'react';

const Rhombus = ({ size, color, delay, duration }) => {
  const rhombusRef = useRef(null);

  useEffect(() => {
    const rhombus = rhombusRef.current;
    if (!rhombus) return;

    // Random initial position
    const startX = Math.random() * 100;
    const startY = Math.random() * 100;

    // Animation
    const animate = () => {
      const time = (Date.now() * 0.001 + delay) % duration;
      const progress = time / duration;
      
      // Floating movement
      const x = startX + Math.sin(progress * Math.PI * 2) * 10;
      const y = startY + Math.cos(progress * Math.PI * 2) * 5;
      
      // Rotation
      const rotation = progress * 360;
      
      rhombus.style.transform = `translate(${x}vw, ${y}vh) rotate(${rotation}deg)`;
      requestAnimationFrame(animate);
    };

    animate();
  }, [delay, duration]);

  return (
    <div 
      ref={rhombusRef}
      className="rhombus" 
      style={{
        width: `${size}px`,
        height: `${size}px`,
        backgroundColor: color,
        opacity: 0.7,
        position: 'absolute',
        filter: 'blur(1px)'
      }}
    />
  );
};

export default Rhombus;