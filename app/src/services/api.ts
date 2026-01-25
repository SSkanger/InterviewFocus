// src/services/api.ts - API服务，与后端通信
import axios from 'axios';

// API基础URL - 使用相对路径，通过Vite代理访问后端
const API_BASE_URL = '';

// 创建axios实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证token等
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// API接口定义 - 匹配后端实际返回的数据结构
export interface InterviewStatus {
  data: {
    attention_score: number;
    gaze_status: string;
    pose_status: string;
    gesture_status: string;
    face_detected: boolean;
    gaze_away_count: number;
    pose_issue_count: number;
    gesture_count: number;
    session_time: number;
    feedback: string;
  };
  is_running: boolean;
}

export interface ApiResponse {
  success: boolean;
  message: string;
}

// API方法
export const api = {
  // 开始面试
  startInterview: (position?: string): Promise<ApiResponse> => {
    return apiClient.post('/api/start', { position });
  },

  // 停止面试
  stopInterview: (): Promise<ApiResponse> => {
    return apiClient.post('/api/stop');
  },

  // 获取状态
  getStatus: (): Promise<InterviewStatus> => {
    return apiClient.get('/api/status');
  },

  // 获取视频流URL - 使用绝对路径，因为视频流不能通过代理
  getVideoStreamUrl: (): string => {
    return 'http://127.0.0.1:5000/api/video_feed';
  },

  // 获取快照 - 使用绝对路径，因为快照不能通过代理
  getSnapshot: (): Promise<{ success: boolean; image?: string; message?: string }> => {
    return axios.get('http://127.0.0.1:5000/api/snapshot', {
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  },
};

export default api;