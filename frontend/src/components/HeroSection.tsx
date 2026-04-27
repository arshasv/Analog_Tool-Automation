import { Link } from 'react-router-dom'
import './HeroSection.css'

export default function HeroSection() {
  return (
    <section className="hero">
      <div className="hero-content">
        <h1 className="hero-title">xEDA</h1>
        <h2 className="hero-subtitle">Analog Design Automation</h2>
        <p className="hero-description">Simulate, Optimize, and Automate with AI</p>
        <div className="hero-cta">
          <Link to="/dashboard" className="cta-button primary">
            Start Designing
          </Link>
          <button className="cta-button secondary" onClick={() => alert('Upload circuit feature coming soon')}>
            Upload Circuit
          </button>
        </div>
      </div>
    </section>
  )
}
