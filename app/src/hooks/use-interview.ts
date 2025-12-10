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
      const response = await api.getStatus();
      if (mountedRef.current) {
        setIsRunning(response.is_running);
        setStatus(response.data);
        setError(null);
      }
    } catch (err) {
      if (mountedRef.current) {
        console.error('获取状态失败:', err);
        setError('无法连接到服务器');
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
        // 开始定期获取状态
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
    fetchStatus();
    
    return () => {
      mountedRef.current = false;
      clearStatusInterval();
    };
  }, [fetchStatus, clearStatusInterval]);

  // 当面试状态改变时，更新定时器
  useEffect(() => {
    if (isRunning && !intervalRef.current) {
      intervalRef.current = setInterval(fetchStatus, 1000);
    } else if (!isRunning && intervalRef.current) {
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