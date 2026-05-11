import { Link, useLocation } from 'react-router-dom';
import BackendStatus from './BackendStatus';
import { useTheme } from '../hooks/useTheme';
import { Home } from 'lucide-react';
import './Navbar.css';

export default function Navbar() {
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();

  const isLandingPage = location.pathname === '/';

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          xEDA
        </Link>
        <div className="navbar-right">
          <BackendStatus />
          {!isLandingPage && (
            <Link to="/" className="navbar-home-icon-link" aria-label="Home">
              <Home size={20} />
            </Link>
          )}
          <button onClick={toggleTheme} className="theme-toggle" aria-label="Toggle theme">
            <span>
              {theme === 'light' ? '☾' : '☼'}
            </span>
          </button>
        </div>
      </div>
    </nav>
  );
}
