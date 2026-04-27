import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import MainLayout from '@layouts/MainLayout';
import Home from '@pages/Home';
import Dashboard from '@pages/Dashboard';
import './App.css';

function App() {
  return (
    <Router>
      <MainLayout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </MainLayout>
    </Router>
  );
}

export default App;
