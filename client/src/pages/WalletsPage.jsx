import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import FuturisticPage from '../components/Layout/FuturisticPage';
// import './WalletsPage.css';

const WalletRiskPage = () => {
  const [walletAddress, setWalletAddress] = useState('');
  const [report, setReport] = useState('');
  const [step, setStep] = useState('input'); // input, analyzing, result
  const [bufferText, setBufferText] = useState('');
  const [bufferIndex, setBufferIndex] = useState(0);
  const [isBuffering, setIsBuffering] = useState(false);

  const analysisBufferTexts = [
    "Analyzing Code Embeddings...",
    "Accessing Heatmaps...",
    "Evaluating Vulnerability Surface...",
    "Mapping Code Structure...",
    "Fetching Context...",
    "Generating Summary...",
    "Finalizing Markdown Content..."
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
    if (!walletAddress.trim()) {
      alert('Please enter a valid wallet address');
      return;
    }
    
    setStep('analyzing');
    setIsBuffering(true);
    setReport('');

    try {
      const response = await fetch('http://localhost:8000/wallet_score', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ wallet_address: walletAddress }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setReport(data.report);
      setIsBuffering(false);
      setStep('result');
    } catch (error) {
      console.error('Error analyzing wallet:', error);
      setIsBuffering(false);
      alert('Failed to analyze wallet. Please try again.');
      setStep('input');
    }
  };

  const resetAnalysis = () => {
    setWalletAddress('');
    setReport('');
    setStep('input');
  };

  return (
    <FuturisticPage>
      <div className="wallet-risk-analyzer">
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
            <h1 className="main-title">Wallet Risk Analyzer</h1>
            <p className="subtitle">Enter a wallet address to assess risk factors and security score</p>
            
            <div className="input-container">
              <input
                type="text"
                placeholder="Enter wallet address (0x...)"
                value={walletAddress}
                onChange={(e) => setWalletAddress(e.target.value)}
                className="wallet-input"
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
                disabled={!walletAddress.trim()}
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
                Analyze Wallet
              </button>
            </div>
          </div>
        )}

        {/* Result Step */}
        {step === 'result' && (
          <div className="result-section">
            <div className="report-header">
              <h2 className="section-title">Wallet Risk Report</h2>
              <div className="wallet-address">{walletAddress}</div>
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
                Analyze Another Wallet
              </button>
            </div>
          </div>
        )}
      </div>
    </FuturisticPage>
  );
};

export default WalletRiskPage;