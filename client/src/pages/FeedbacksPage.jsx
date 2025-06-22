import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import FuturisticPage from '../components/Layout/FuturisticPage';

const FeedbackLoopPage = () => {
  const [formData, setFormData] = useState({
    query: '',
    walletAddress: '',
    tokenAddress: '',
    amount: ''
  });
  const [report, setReport] = useState('');
  const [step, setStep] = useState('input'); // input, analyzing, result, completed
  const [bufferText, setBufferText] = useState('');
  const [bufferIndex, setBufferIndex] = useState(0);
  const [isBuffering, setIsBuffering] = useState(false);
  const [completionMessage, setCompletionMessage] = useState('');

  const analysisBufferTexts = [
    "Fetching User Transactions...",
    "Finding Potential Malicious Transactions...",
    "Analyzing Background Wallets...",
    "Fetching Cryptocurrency Flows...",
    "Checking Recursive Requirements...",
    "Handling Currency Transfers...",
    "Generating Report...",
    "Finalising Feedback Loop...",
    "Creating Summary Report..."
  ];

  // Buffer animation effect
  useEffect(() => {
    if (isBuffering) {
      const interval = setInterval(() => {
        setBufferIndex((prev) => (prev + 1) % analysisBufferTexts.length);
      }, 6000);
      return () => clearInterval(interval);
    }
  }, [isBuffering]);

  useEffect(() => {
    if (isBuffering) {
      setBufferText(analysisBufferTexts[bufferIndex]);
    }
  }, [bufferIndex, isBuffering]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.query.trim()) {
      alert('Please enter your feedback query');
      return;
    }
    
    setStep('analyzing');
    setIsBuffering(true);
    setReport('');

    try {
      const response = await fetch('http://localhost:8000/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          fdata: formData.query,
          wallet_address: formData.walletAddress || "",
          token_address: formData.tokenAddress || "",
          amt: formData.amount || ""
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setReport(data.report);
      setIsBuffering(false);
      setStep('result');
    } catch (error) {
      console.error('Error submitting feedback:', error);
      setIsBuffering(false);
      alert('Failed to process feedback. Please try again.');
      setStep('input');
    }
  };

  const handleAgree = () => {
    setCompletionMessage("Wallet Addresses have been marked and flagged");
    setStep('completed');
  };

  const handleDisagree = () => {
    setStep('input');
    setReport('');
  };

  const resetForm = () => {
    setFormData({
      query: '',
      walletAddress: '',
      tokenAddress: '',
      amount: ''
    });
    setCompletionMessage('');
    setStep('input');
  };

return (
    <FuturisticPage>
        <div className="feedback-loop-container">
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
                    <h1 className="main-title">Feedback Loop</h1>
                    <p className="subtitle">Submit your query about suspicious activity</p>
                    
                    <form onSubmit={handleSubmit} className="feedback-form">
                        <div className="form-group">
                            <label>Feedback Query*</label>
                            <textarea
                                name="query"
                                placeholder="Describe the suspicious activity or concern..."
                                value={formData.query}
                                onChange={handleChange}
                                required
                                rows={4}
                            />
                        </div>

                        <div className="form-group">
                            <label>Wallet Address*</label>
                            <input
                                type="text"
                                name="walletAddress"
                                placeholder="0x..."
                                value={formData.walletAddress}
                                onChange={handleChange}
                            />
                        </div>

                        <div className="form-group">
                            <label>Token Address</label>
                            <input
                                type="text"
                                name="tokenAddress"
                                placeholder="0x... (optional)"
                                value={formData.tokenAddress}
                                onChange={handleChange}
                            />
                        </div>

                        <div className="form-group">
                            <label>Amount (with unit)</label>
                            <input
                                type="text"
                                name="amount"
                                placeholder="e.g., 1000 USDC (optional)"
                                value={formData.amount}
                                onChange={handleChange}
                            />
                        </div>

                        <button type="submit" className="submit-btn">
                            Submit Feedback
                        </button>
                    </form>
                </div>
            )}

            {/* Result Step */}
            {step === 'result' && (
                <div className="result-section">
                    <h2 className="section-title">Feedback Analysis Report</h2>
                    
                    <div className="markdown-content">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                            {report}
                        </ReactMarkdown>
                    </div>

                    <div className="button-container">
                        <button onClick={handleAgree} className="action-btn yes-btn">
                            Agree
                        </button>
                        <button onClick={handleDisagree} className="action-btn no-btn">
                            Disagree
                        </button>
                    </div>
                </div>
            )}

            {/* Completion Step */}
            {step === 'completed' && (
                <div className="completed-section">
                    <div className="completion-message">
                        {completionMessage}
                    </div>
                    <button onClick={resetForm} className="action-btn">
                        Submit New Feedback
                    </button>
                </div>
            )}
        </div>

        <style jsx>{`
            .feedback-loop-container {
                position: relative;
                width: 100%;
                min-height: 100vh;
                color: #ffffff;
                padding: 2rem;
                max-width: 800px;
                margin: 0 auto;
                overflow-y: auto; /* Enable vertical scrolling */
                max-height: 100vh; /* Limit to viewport height */
                padding-bottom: 10rem; /* Add space at bottom */
                /* Hide scrollbars for all browsers */
                scrollbar-width: none; /* Firefox */
                -ms-overflow-style: none;  /* IE and Edge */
            }
            .feedback-loop-container::-webkit-scrollbar {
                display: none; /* Chrome, Safari, Opera */
            }

            .markdown-content {
                background: rgba(15, 15, 26, 0.8);
                padding: 1.5rem;
                border-radius: 8px;
                border: 1px solid rgba(0, 209, 255, 0.2);
                margin-bottom: 2rem;
                line-height: 1.6;
                max-height: 50vh; /* Limit height and enable scroll */
                overflow-y: auto;
                /* Hide scrollbars for all browsers */
                scrollbar-width: none; /* Firefox */
                -ms-overflow-style: none;  /* IE and Edge */
            }
            .markdown-content::-webkit-scrollbar {
                display: none; /* Chrome, Safari, Opera */
            }

            .buffer-overlay {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(15, 15, 26, 0.95);
                backdrop-filter: blur(10px);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 1000;
                flex-direction: column;
            }

            .buffer-content {
                text-align: center;
                color: #00d1ff;
                padding: 2rem;
                border-radius: 16px;
                background: rgba(26, 26, 46, 0.8);
                box-shadow: 0 8px 32px rgba(0, 209, 255, 0.2);
                border: 1px solid rgba(0, 209, 255, 0.1);
                max-width: 500px;
                width: 90%;
            }

            .buffer-spinner {
                width: 80px;
                height: 80px;
                border: 5px solid rgba(0, 209, 255, 0.1);
                border-top: 5px solid #00d1ff;
                border-radius: 50%;
                animation: spin 1.5s linear infinite;
                margin: 0 auto 30px;
            }

            .buffer-text {
                font-size: 1.5rem;
                font-weight: 500;
                margin-top: 1rem;
                background: linear-gradient(90deg, #00d1ff, #00ffaa);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                animation: pulse 2s ease-in-out infinite;
            }

            .input-section {
                text-align: center;
                padding: 2rem;
                background: rgba(26, 26, 46, 0.6);
                border-radius: 16px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.05);
                margin-top: 1rem;
            }

            .main-title {
                font-size: 2.5rem;
                font-weight: 700;
                background: linear-gradient(135deg, #00d1ff 0%, #00ffaa 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 1rem;
            }

            .subtitle {
                font-size: 1.1rem;
                color: rgba(255, 255, 255, 0.7);
                margin-bottom: 2rem;
            }

            .feedback-form {
                display: flex;
                flex-direction: column;
                gap: 1.5rem;
                text-align: left;
            }

            .form-group {
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
            }

            .form-group label {
                font-size: 1rem;
                color: rgba(255, 255, 255, 0.8);
            }

            .form-group input,
            .form-group textarea {
                width: 100%;
                padding: 1rem;
                border-radius: 8px;
                border: 1px solid rgba(0, 209, 255, 0.3);
                background: rgba(15, 15, 26, 0.8);
                color: #ffffff;
                font-size: 1rem;
                transition: all 0.3s ease;
            }

            .form-group textarea {
                min-height: 120px;
                resize: vertical;
            }

            .form-group input:focus,
            .form-group textarea:focus {
                outline: none;
                border-color: #00d1ff;
                box-shadow: 0 0 0 2px rgba(0, 209, 255, 0.2);
            }

            .submit-btn {
                background: linear-gradient(135deg, #00d1ff 0%, #00ffaa 100%);
                color: #0f0f1a;
                border: none;
                padding: 1rem 2rem;
                border-radius: 8px;
                font-size: 1.1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                margin-top: 1rem;
            }

            .submit-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(0, 209, 255, 0.3);
            }

            .result-section {
                padding: 2rem;
                background: rgba(26, 26, 46, 0.6);
                border-radius: 16px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.05);
                margin-top: 1rem;
            }

            .section-title {
                font-size: 2rem;
                font-weight: 600;
                color: #00d1ff;
                margin-bottom: 1.5rem;
                text-align: center;
            }

            .button-container {
                display: flex;
                justify-content: center;
                margin-top: 2rem;
            }

            .action-btn {
                padding: 0.8rem 1.5rem;
                font-size: 1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                border: none;
            }

            .yes-btn {
                background: rgba(0, 255, 128, 0.15);
                color: #00cc60;
                border-radius: 10px 0 0 10px;
                border: 1px solid #00cc60;
            }

            .yes-btn:hover {
                background: rgba(2, 149, 73, 0.636);
                color: #dbdfdd;
                border-radius: 10px 0 0 10px;
                border: 1px solid #00cc60;
            }

            .no-btn {
                background: rgba(161, 4, 4, 0.15);
                color: #cd5959;
                border-radius: 0 10px 10px 0;
                border: 1px solid #ff0000;
            }

            .no-btn:hover {
                background: rgba(209, 48, 48, 0.574);
                color: #e8c7c7;
                border-radius: 0 10px 10px 0;
                border: 1px solid #ff0000;
            }

            .completed-section {
                text-align: center;
                padding: 2rem;
                background: rgba(26, 26, 46, 0.6);
                border-radius: 16px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.05);
                margin-top: 1rem;
            }

            .completion-message {
                font-size: 1.5rem;
                color: #00ffaa;
                margin-bottom: 2rem;
                padding: 1rem;
                background: rgba(0, 255, 128, 0.1);
                border-radius: 8px;
                border: 1px solid #00cc60;
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            @keyframes pulse {
                0%, 100% { opacity: 0.8; }
                50% { opacity: 1; }
            }
        `}</style>
    </FuturisticPage>
);
};

export default FeedbackLoopPage;