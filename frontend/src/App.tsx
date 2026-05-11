import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import MainLayout from '@layouts/MainLayout';
import Home from '@pages/Home';
import Dashboard from '@pages/Dashboard';
import { ThemeProvider } from './hooks/useTheme';
import { Toaster } from 'react-hot-toast';
import './styles/themes.css';
import './App.css';

function App() {
  return (
    <ThemeProvider>
      <Toaster position="top-right" toastOptions={{
        style: {
          background: 'var(--card-bg)',
          color: 'var(--text-main)',
          border: '1px solid var(--border)',
        }
      }} />
      <Router>
        <MainLayout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/dashboard" element={<Dashboard />} />
          </Routes>
        </MainLayout>
      </Router>
    </ThemeProvider>
  );
}

export default App;
