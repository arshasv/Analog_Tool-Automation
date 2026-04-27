type FeatureCardProps = {
  title: string;
  description: string;
};

const FeatureCard = ({ title, description }: FeatureCardProps): JSX.Element => {
  return (
    <article className="card" aria-label={title}>
      <h3>{title}</h3>
      <p>{description}</p>
    </article>
  );
};

export default FeatureCard;
