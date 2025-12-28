// src/hooks/use-interview.ts - 面试状态管理Hook
import { useState, useEffect, useCallback, useRef } from 'react';
import { api, InterviewStatus } from '@/services/api';

interface UseInterviewReturn {
  isRunning: boolean;
  status: InterviewStatus['data'] | null;
  startInterview: () => Promise<void>;
  stopInterview: () => Promise<void>;
  error: string | null;
  isLoading: boolean;
}

export const useInterview = (): UseInterviewReturn => {
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [status, setStatus] = useState<InterviewStatus['data'] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const mountedRef = useRef<boolean>(true);

  // 清理定时器
  const clearStatusInterval = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  // 获取状态
  const fetchStatus = useCallback(async () => {
    try {
      console.log('开始获取状态...');
      const response = await api.getStatus();
      console.log('API原始响应:', response); // 添加更详细的调试日志
      
      if (!mountedRef.current) return;
      
      // 检查响应结构并正确提取数据
      if (response && typeof response === 'object') {
        // 后端返回的结构是 {data: {...}, is_running: boolean}
        // 由于axios响应拦截器已经提取了response.data，所以这里的response就是完整的InterviewStatus对象
        const extractedData = {
          attention_score: response.data?.attention_score || 0,
          gaze_status: response.data?.gaze_status || '未知',
          pose_status: response.data?.pose_status || '未知',
          gesture_status: response.data?.gesture_status || '未知',
          face_detected: response.data?.face_detected || false,
          gaze_away_count: response.data?.gaze_away_count || 0,
          pose_issue_count: response.data?.pose_issue_count || 0,
          gesture_count: response.data?.gesture_count || 0,
          session_time: response.data?.session_time || 0,
          feedback: response.data?.feedback || '系统运行中...'
        };
        
        console.log('提取的数据:', extractedData);
        console.log('is_running状态:', response.is_running);
        console.log('face_detected状态:', extractedData.face_detected);
        console.log('attention_score:', extractedData.attention_score);
        
        // 更新状态 - 确保状态更新
        setIsRunning(response.is_running || false);
        setStatus(extractedData);
        setError(null);
      } else {
        console.error('API响应格式不正确:', response);
        setError('服务器响应格式错误');
        // 设置默认状态
        setStatus({
          attention_score: 0,
          gaze_status: '未知',
          pose_status: '未知',
          gesture_status: '未知',
          face_detected: false,
          gaze_away_count: 0,
          pose_issue_count: 0,
          gesture_count: 0,
          session_time: 0,
          feedback: '无法获取状态'
        });
      }
    } catch (err) {
      if (mountedRef.current) {
        console.error('获取状态失败:', err);
        console.error('错误详情:', err.message);
        setError('无法连接到服务器');
        // 设置错误状态
        setStatus({
          attention_score: 0,
          gaze_status: '错误',
          pose_status: '错误',
          gesture_status: '错误',
          face_detected: false,
          gaze_away_count: 0,
          pose_issue_count: 0,
          gesture_count: 0,
          session_time: 0,
          feedback: '连接失败'
        });
      }
    }
  }, []);

  // 开始面试
  const startInterview = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await api.startInterview();
      if (response.success) {
        setIsRunning(true);
        // 立即获取一次状态
        await fetchStatus();
        // 然后开始定期获取状态
        intervalRef.current = setInterval(fetchStatus, 1000);
      } else {
        setError(response.message || '开始面试失败');
      }
    } catch (err) {
      console.error('开始面试失败:', err);
      setError('开始面试失败');
    } finally {
      setIsLoading(false);
    }
  }, [fetchStatus]);

  // 停止面试
  const stopInterview = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await api.stopInterview();
      if (response.success) {
        setIsRunning(false);
        // 停止定期获取状态
        clearStatusInterval();
      } else {
        setError(response.message || '停止面试失败');
      }
    } catch (err) {
      console.error('停止面试失败:', err);
      setError('停止面试失败');
    } finally {
      setIsLoading(false);
    }
  }, [clearStatusInterval]);

  // 组件挂载时获取初始状态
  useEffect(() => {
    console.log('组件挂载，获取初始状态...');
    fetchStatus();
    
    return () => {
      mountedRef.current = false;
      clearStatusInterval();
    };
  }, [fetchStatus, clearStatusInterval]);

  // 当面试状态改变时，更新定时器
  useEffect(() => {
    console.log('面试状态改变:', isRunning);
    if (isRunning && !intervalRef.current) {
      console.log('启动定时器，每秒获取状态');
      intervalRef.current = setInterval(fetchStatus, 1000);
    } else if (!isRunning && intervalRef.current) {
      console.log('停止定时器');
      clearStatusInterval();
    }
    
    return () => {
      clearStatusInterval();
    };
  }, [isRunning, fetchStatus, clearStatusInterval]);

  return {
    isRunning,
    status,
    startInterview,
    stopInterview,
    error,
    isLoading,
  };
};