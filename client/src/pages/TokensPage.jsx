import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import FuturisticPage from '../components/Layout/FuturisticPage';
// import './TokensPage.css';

const TokenScorePage = () => {
  const [tokenAddress, setTokenAddress] = useState('');
  const [report, setReport] = useState('');
  const [step, setStep] = useState('input'); // input, analyzing, result
  const [bufferText, setBufferText] = useState('');
  const [bufferIndex, setBufferIndex] = useState(0);
  const [isBuffering, setIsBuffering] = useState(false);

  const analysisBufferTexts = [
    "Analyzing Token Metrics...",
    "Checking Liquidity Pools...",
    "Assessing Market Performance...",
    "Calculating Risk Factors...",
    "Generating Token Report..."
  ];

  // Buffer animation effect
  useEffect(() => {
    if (isBuffering) {
      const interval = setInterval(() => {
        setBufferIndex((prev) => (prev + 1) % analysisBufferTexts.length);
      }, 2000);
      return () => clearInterval(interval);
    }
  }, [isBuffering]);

  useEffect(() => {
    if (isBuffering) {
      setBufferText(analysisBufferTexts[bufferIndex]);
    }
  }, [bufferIndex, isBuffering]);

  const handleAnalyze = async () => {
    if (!tokenAddress.trim()) {
      alert('Please enter a valid token address');
      return;
    }
    
    setStep('analyzing');
    setIsBuffering(true);
    setReport('');

    try {
      const response = await fetch('http://localhost:8000/token_score', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token_address: tokenAddress }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setReport(data.report);
      setIsBuffering(false);
      setStep('result');
    } catch (error) {
      console.error('Error analyzing token:', error);
      setIsBuffering(false);
      alert('Failed to analyze token. Please try again.');
      setStep('input');
    }
  };

  const resetAnalysis = () => {
    setTokenAddress('');
    setReport('');
    setStep('input');
  };

  return (
    <FuturisticPage>
      <div className="token-score-analyzer">
        {/* Buffer Overlay */}
        {isBuffering && (
          <div className="buffer-overlay">
            <div className="buffer-content">
              <div className="buffer-spinner"></div>
              <div className="buffer-text">{bufferText}</div>
            </div>
          </div>
        )}

        {/* Input Step */}
        {step === 'input' && (
          <div className="input-section">
            <h1 className="main-title">Token Score Analyzer</h1>
            <p className="subtitle">Enter a token address to assess security and performance metrics</p>
            
            <div className="input-container">
              <input
                type="text"
                placeholder="Enter token address (0x...)"
                value={tokenAddress}
                onChange={(e) => setTokenAddress(e.target.value)}
                className="token-input"
                style={{
                  width: '100%',
                  maxWidth: '600px',
                  padding: '16px 24px',
                  fontSize: '18px',
                  borderRadius: '12px',
                  border: '2px solid rgba(0, 209, 255, 0.5)',
                  outline: 'none',
                  color: '#ffffff',
                  backgroundColor: 'rgba(15, 15, 26, 0.8)',
                  boxShadow: '0 4px 20px rgba(0, 209, 255, 0.2)',
                  transition: 'all 0.3s ease',
                }}
              />
              <button 
                onClick={handleAnalyze} 
                className="analyze-btn"
                disabled={!tokenAddress.trim()}
                style={{
                  width: '100%',
                  maxWidth: '300px',
                  padding: '16px 32px',
                  fontSize: '18px',
                  fontWeight: '600',
                  borderRadius: '12px',
                  border: 'none',
                  background: 'linear-gradient(135deg, #00d1ff 0%, #00ffaa 100%)',
                  color: '#0f0f1a',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  boxShadow: '0 4px 20px rgba(0, 209, 255, 0.3)',
                  marginTop: '20px',
                  textTransform: 'uppercase',
                  letterSpacing: '1px',
                }}
              >
                Analyze Token
              </button>
            </div>
          </div>
        )}

        {/* Result Step */}
        {step === 'result' && (
          <div className="result-section">
            <div className="report-header">
              <h2 className="section-title">Token Score Report</h2>
              <div className="token-address">{tokenAddress}</div>
            </div>
            
            <div className="markdown-content">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {report}
              </ReactMarkdown>
            </div>

            <div className="button-container">
              <button 
                onClick={resetAnalysis} 
                className="action-btn"
              >
                Analyze Another Token
              </button>
            </div>
          </div>
        )}
      </div>
    </FuturisticPage>
  );
};

export default TokenScorePage;