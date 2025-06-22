import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'prism-react-renderer';
import FuturisticPage from '../components/Layout/FuturisticPage';
import './ContractsPage.css';

const HomePage = () => {
  const [step, setStep] = useState('upload'); // upload, analyzing, result, updating, final
  const [file, setFile] = useState(null);
  const [fileName, setFileName] = useState('');
  const [solCode, setSolCode] = useState('');
  const [summary, setSummary] = useState('');
  const [updatedCode, setUpdatedCode] = useState('');
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

  const updateBufferTexts = [
    "Blending New Changes...",
    "Validating Code Integrity...",
    "Finalizing Updates...",
  ];

  // Buffer animation effect
  useEffect(() => {
    if (isBuffering) {
      const currentTexts = step === 'analyzing' ? analysisBufferTexts : updateBufferTexts;
      const interval = setInterval(() => {
        setBufferIndex((prev) => (prev + 1) % currentTexts.length);
      }, 3000);
      return () => clearInterval(interval);
    }
  }, [isBuffering, step]);

  useEffect(() => {
    if (isBuffering) {
      const currentTexts = step === 'analyzing' ? analysisBufferTexts : updateBufferTexts;
      setBufferText(currentTexts[bufferIndex]);
    }
  }, [bufferIndex, isBuffering, step]);

  const handleFileUpload = (event) => {
    const uploadedFile = event.target.files[0];
    if (uploadedFile && uploadedFile.name.endsWith('.sol')) {
      setFile(uploadedFile);
      setFileName(uploadedFile.name);
      
      const reader = new FileReader();
      reader.onload = (e) => {
        setSolCode(e.target.result);
      };
      reader.readAsText(uploadedFile);
    } else {
      alert('Please select a .sol file');
    }
  };

  const analyzeContract = async () => {
    if (!solCode) return;
    
    setStep('analyzing');
    setIsBuffering(true);
    
    try {
      const response = await fetch('http://localhost:8000/smart_contract', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ contract: solCode }),
      });
      
      const data = await response.json();
      setSummary(data.summary);
      setIsBuffering(false);
      setStep('result');
    } catch (error) {
      console.error('Error analyzing contract:', error);
      setIsBuffering(false);
      alert('Error analyzing contract. Please try again.');
    }
  };

  const handleYes = async () => {
    setStep('updating');
    setIsBuffering(true);
    
    try {
      const response = await fetch('http://localhost:8000/update_code', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          code: solCode, 
          changes: summary 
        }),
      });
      
      const data = await response.json();
      setUpdatedCode(data.updated_code);
      setIsBuffering(false);
      setStep('final');
    } catch (error) {
      console.error('Error updating code:', error);
      setIsBuffering(false);
      alert('Error updating code. Please try again.');
    }
  };

  const handleNo = () => {
    setStep('upload');
    setFile(null);
    setFileName('');
    setSolCode('');
    setSummary('');
    setUpdatedCode('');
  };

  const downloadFile = () => {
    const blob = new Blob([updatedCode], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName || 'updated_contract.sol';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const MarkdownRenderer = ({ content }) => (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        code({ children, ...props }) {
          return <code {...props}>{children}</code>;
        },
        h1: ({node, ...props}) => <h1 className="markdown-h1" {...props} />,
        h2: ({node, ...props}) => <h2 className="markdown-h2" {...props} />,
        h3: ({node, ...props}) => <h3 className="markdown-h3" {...props} />,
        p: ({node, ...props}) => <p className="markdown-p" {...props} />,
        strong: ({node, ...props}) => <strong className="markdown-bold" {...props} />,
        em: ({node, ...props}) => <em className="markdown-italic" {...props} />,
        a: ({node, ...props}) => <a className="markdown-link" target="_blank" rel="noopener noreferrer" {...props} />,
        ul: ({node, ...props}) => <ul className="markdown-ul" {...props} />,
        ol: ({node, ...props}) => <ol className="markdown-ol" {...props} />,
        li: ({node, ...props}) => <li className="markdown-li" {...props} />,
        blockquote: ({node, ...props}) => <blockquote className="markdown-blockquote" {...props} />,
        table: ({node, ...props}) => <div className="markdown-table-container"><table className="markdown-table" {...props} /></div>
      }}
    >
      {content}
    </ReactMarkdown>
  );

  return (
    <FuturisticPage>
      <div className="smart-contract-analyzer">
        {/* Buffer Overlay */}
        {isBuffering && (
          <div className="buffer-overlay">
            <div className="buffer-content">
              <div className="buffer-spinner"></div>
              <div className="buffer-text">{bufferText}</div>
            </div>
          </div>
        )}

        {/* Upload Step */}
        {step === 'upload' && (
          <div className="upload-section">
            <h1 className="main-title">Smart Contract Analyzer</h1>
            <p className="subtitle">Upload your Solidity contract for analysis and optimization</p>
            
            <div className="file-upload-container">
              <input
                type="file"
                accept=".sol"
                onChange={handleFileUpload}
                className="file-input"
                id="sol-file"
              />
              <label htmlFor="sol-file" className="file-upload-label">
                <div className="upload-icon">📄</div>
                <div className="upload-text">
                  {file ? fileName : 'Choose .sol file'}
                </div>
              </label>
            </div>

            {file && (
              <button onClick={analyzeContract} className="analyze-btn">
                Analyze Contract
              </button>
            )}
          </div>
        )}

        {/* Result Step */}
        {step === 'result' && (
          <div className="result-section">
            <h2 className="section-title">Analysis Complete</h2>
            <div className="markdown-content">
              <MarkdownRenderer content={summary} />
            </div>
            
            <div className="button-container">
              <button onClick={handleYes} className="action-btn yes-btn">
                Apply Changes
              </button>
              <button onClick={handleNo} className="action-btn no-btn">
                Reject Changes
              </button>
            </div>
          </div>
        )}

        {/* Final Step */}
        {step === 'final' && (
          <div className="final-section">
            <h2 className="section-title">Code Updated Successfully</h2>
            <pre className="code-preview">{updatedCode}</pre>
            <button onClick={downloadFile} className="download-btn">
              Download Updated Contract
            </button>
          </div>
        )}
      </div>
    </FuturisticPage>
  );
};

export default HomePage;