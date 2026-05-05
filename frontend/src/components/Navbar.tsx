import { Link } from 'react-router-dom';
import BackendStatus from './BackendStatus';
import { useTheme } from '../hooks/useTheme';
import './Navbar.css';

export default function Navbar() {
  const { theme, toggleTheme } = useTheme();

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          xEDA
        </Link>
        <div className="navbar-right">
          <BackendStatus />
          <ul className="navbar-menu">
            <li>
              <Link to="/">Home</Link>
            </li>
          </ul>
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
