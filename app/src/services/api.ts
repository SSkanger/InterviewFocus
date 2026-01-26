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

// 注意力历史记录项
export interface AttentionHistoryItem {
  timestamp: number;
  score: number;
  face_score: number;
  gaze_score: number;
  posture_score: number;
  gesture_score: number;
}

// 注意力分析数据
export interface AttentionAnalysis {
  attention_score: number;
  attention_states: {
    high: number;
    medium: number;
    low: number;
    face_missing: number;
  };
  scoring_criteria: {
    face_detection: {
      weight: number;
      description: string;
      current_status: string;
      average_score?: number;
    };
    gaze_direction: {
      weight: number;
      description: string;
      current_status: string;
      average_score?: number;
    };
    posture: {
      weight: number;
      description: string;
      current_status: string;
      average_score?: number;
    };
    gesture: {
      weight: number;
      description: string;
      current_status: string;
      average_score?: number;
    };
  };
  recommendations: string[];
  statistics: {
    gaze_away_count: number;
    pose_issue_count: number;
    gesture_count: number;
    session_time: number;
    total_records?: number;
    attention_state_ratios?: {
      high: number;
      medium: number;
      low: number;
      face_missing: number;
    };
  };
  interview_summary?: string;
  status?: string;
  message?: string;
}

// 注意力历史数据响应
export interface AttentionHistoryResponse {
  success: boolean;
  message: string;
  data: {
    history: AttentionHistoryItem[];
    analysis: {
      average_score: number;
      max_score: number;
      min_score: number;
      average_face_score: number;
      average_gaze_score: number;
      average_posture_score: number;
      average_gesture_score: number;
      total_records: number;
    };
  };
}

// 注意力分析响应
export interface AttentionAnalysisResponse {
  success: boolean;
  message: string;
  data: AttentionAnalysis;
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

  // 获取注意力历史数据
  getAttentionHistory: (): Promise<AttentionHistoryResponse> => {
    return apiClient.get('/api/attention/history');
  },

  // 获取注意力分析报告
  getAttentionAnalysis: (): Promise<AttentionAnalysisResponse> => {
    return apiClient.get('/api/attention/analysis');
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