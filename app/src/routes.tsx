import InterviewSimulation from './pages/InterviewSimulation';
import type { ReactNode } from 'react';

interface RouteConfig {
  name: string;
  path: string;
  element: ReactNode;
  visible?: boolean;
}

const routes: RouteConfig[] = [
  {
    name: '智能面试模拟',
    path: '/',
    element: <InterviewSimulation />
  }
];

export default routes;
