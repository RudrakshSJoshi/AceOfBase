// src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/HomePage';
import ContractsPage from './pages/ContractsPage';
import WalletsPage from './pages/WalletsPage';
import TokensPage from './pages/TokensPage';
import FeedbacksPage from './pages/FeedbacksPage';
import AboutPage from './pages/AboutPage';
import ContactPage from './pages/ContactPage';
import NotFoundPage from './pages/NotFoundPage';

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/contracts" element={<ContractsPage />} />
        <Route path="/wallets" element={<WalletsPage />} />
        <Route path="/tokens" element={<TokensPage />} />
        <Route path="/feedbacks" element={<FeedbacksPage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/contact" element={<ContactPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </Router>
  );
};

export default App;