import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './HomePage.css';

const tools = [
  {
    name: 'contracts',
    title: 'Smart Contract Auditor',
    description: 'Leverages Attention Gradient Back Propagation with Code Heatmap Visualization and AgenticAI-powered Semantic Analysis for comprehensive vulnerability surface mapping.'
  },
  {
    name: 'wallets',
    title: 'Wallet Anomaly Detection',
    description: 'Graph Neural Network architecture powered by AgenticAI that performs deep behavioral analysis and threat modeling to generate dynamic risk scoring matrices.'
  },
  {
    name: 'tokens',
    title: 'Token Threat Risk Assessment',
    description: 'AgenticAI-driven behavioral forensics combining on-chain pattern recognition with web-crawled threat intelligence to detect rug pulls, honeypots, and sophisticated economic exploits.'
  },
  {
    name: 'feedbacks',
    title: 'Feedback Loop Deep Research',
    description: 'Implements recursive graph traversal algorithms with malicious node identification protocols to trace adversarial patterns across blockchain transaction networks.'
  }
];

const Home = () => {
  // Check sessionStorage for whether intro has been shown
  const [showIntro, setShowIntro] = useState(() => {
    return sessionStorage.getItem('introShown') !== 'true';
  });

  const [currentToolIndex, setCurrentToolIndex] = useState(0);
  const [dots, setDots] = useState('');
  const [fadeOut, setFadeOut] = useState(false);
  const slideTexts = [
    "Autonomous AI agents securing the Base blockchain",
    "Agentic intelligence meets smart contract protection",
    "Graph-based wallet risk analysis in real-time",
    "Next-gen token safety and scam prevention powered by AI"
  ];
  const [currentSlide, setCurrentSlide] = useState(0);

  useEffect(() => {
    // Intro animation with dots
    if (showIntro) {
      const introTimeout = setTimeout(() => {
        setFadeOut(true);
        setTimeout(() => {
          setShowIntro(false);
          sessionStorage.setItem('introShown', 'true');
        }, 1000);
      }, 3500);
      
      return () => {
        clearTimeout(introTimeout);
      };
    }
  }, [showIntro]);

  useEffect(() => {
    // Text slider animation (now moving right)
    const interval = setInterval(() => {
      setCurrentSlide(prev => (prev + 1) % slideTexts.length);
    }, 3000);
    return () => clearInterval(interval);
  }, [slideTexts.length]);

  const nextTool = () => {
    setCurrentToolIndex(prev => (prev + 1) % tools.length);
  };

  const prevTool = () => {
    setCurrentToolIndex(prev => (prev - 1 + tools.length) % tools.length);
  };

  if (showIntro) {
    return (
      <div className={`intro-container ${fadeOut ? 'fade-out' : ''}`}>
        <div className="intro-text">
          SECURITY REIMAGINED WITH AGENTICAI<span className="dots">{dots}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <nav className="navbar">
        <div className="navbar-logo">McBase Secure</div>
        <div className="navbar-links">
          <Link to="/" className="nav-link">Home</Link>
          <Link to="/about" className="nav-link">About</Link>
          <Link to="/contact" className="nav-link">Contact</Link>
        </div>
      </nav>

      <main className="main-content">
        <div className="header-section">
          <h1 className="main-title">
            BASE INFRA <span className="security-text">SECURITY</span> SUITE
          </h1>
          <div className="slider-container">
            {slideTexts.map((text, index) => (
              <div 
                key={index}
                className={`slider-text ${index === currentSlide ? 'active' : ''}`}
              >
                {text}
              </div>
            ))}
          </div>
        </div>

        <div className="description-box">
          <p>
            Agentic Firewall is an AI-native security suite built for the Base ecosystem, combining autonomous agent-based intelligence with real-time analytics. 
            From smart contract auditing using attention heatmaps to wallet risk scoring with Graph Neural Networks and token scam detection via web crawlers, 
            our tools work synergistically to detect, trace, and neutralize threats in the evolving Web3 environment.
          </p>
        </div>

        <div className="tools-section">
          <div className="rhombus-container">
            <div className="rhombus"></div>
            <div className="rhombus-overlay"></div>
            <div className="floating-icon icon-1"></div>
            <div className="floating-icon icon-2"></div>
            <div className="tool-info">
              <h2>{tools[currentToolIndex].title}</h2>
              <p>{tools[currentToolIndex].description}</p>
              <Link 
                to={`/${tools[currentToolIndex].name}`} 
                className="access-button"
              >
                Access Tool
              </Link>
            </div>
            <button className="nav-arrow left-arrow" onClick={prevTool}>
              <svg viewBox="0 0 24 24" width="24" height="24">
                <path d="M15.41 16.59L10.83 12l4.58-4.59L14 6l-6 6 6 6 1.41-1.41z" fill="currentColor"/>
              </svg>
            </button>
            <button className="nav-arrow right-arrow" onClick={nextTool}>
              <svg viewBox="0 0 24 24" width="24" height="24">
                <path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z" fill="currentColor"/>
              </svg>
            </button>
          </div>
        </div>
      </main>

      <footer className="footer">
        <div className="footer-content">
          <p>© 2023 AgenticAI. All rights reserved.</p>
          <div className="footer-links">
            <a href="#">Privacy Policy</a>
            <a href="#">Terms of Service</a>
            <a href="#">Documentation</a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Home;