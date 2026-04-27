import './FeaturesSection.css'

interface Feature {
  title: string
  description: string
  icon: string
}

const features: Feature[] = [
  {
    title: 'Simulation',
    description: 'Run accurate circuit simulations with industry-standard tools',
    icon: '⚡',
  },
  {
    title: 'Optimization',
    description: 'Automatically optimize circuit parameters for performance',
    icon: '🎯',
  },
  {
    title: 'AI Automation',
    description: 'Leverage AI to accelerate design cycles and reduce iterations',
    icon: '🤖',
  },
]

export default function FeaturesSection() {
  return (
    <section className="features">
      <div className="features-container">
        <h2>Features</h2>
        <div className="features-grid">
          {features.map((feature, index) => (
            <div key={index} className="feature-card">
              <div className="feature-icon">{feature.icon}</div>
              <h3>{feature.title}</h3>
              <p>{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
