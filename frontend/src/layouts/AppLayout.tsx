import type { ReactNode } from 'react';
import Navbar from '../components/Navbar';

type AppLayoutProps = {
  children: ReactNode;
};

const AppLayout = ({ children }: AppLayoutProps): JSX.Element => {
  return (
    <div className="app-shell">
      <Navbar />
      <main className="content">{children}</main>
    </div>
  );
};

export default AppLayout;
