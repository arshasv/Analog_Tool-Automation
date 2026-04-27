import { Link } from 'react-router-dom';
import BackendStatus from './BackendStatus';
import './Navbar.css';

export default function Navbar() {
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
            <li>
              <Link to="/dashboard">Dashboard</Link>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  );
}
