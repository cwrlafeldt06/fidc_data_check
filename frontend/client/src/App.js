import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import FundAnalysis from './pages/FundAnalysis';
import Results from './pages/Results';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Header />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/fund-analysis" element={<FundAnalysis />} />
            <Route path="/results/:jobId" element={<Results />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App; 