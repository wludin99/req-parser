import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';

// TODO: Import components when implemented
// import Home from './pages/Home';
// import Results from './pages/Results';

function App() {
  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <h1>Government Tender Extraction System</h1>
        </header>
        <main>
          <Routes>
            {/* TODO: Add routes when components are implemented */}
            <Route path="/" element={<div>Home page coming soon...</div>} />
            <Route path="/results" element={<div>Results page coming soon...</div>} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
