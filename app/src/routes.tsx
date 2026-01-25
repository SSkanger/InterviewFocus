import InterviewSimulation from './pages/InterviewSimulation';
import VoiceTest from './pages/VoiceTest';
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
  },
  {
    name: '语音功能测试',
    path: '/voice-test',
    element: <VoiceTest />
  }
];

export default routes;
