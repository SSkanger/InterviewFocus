// src/hooks/use-interview.ts - 面试状态管理Hook
import { useState, useEffect, useCallback, useRef } from 'react';
import { api, InterviewStatus, AttentionHistoryResponse, AttentionAnalysisResponse } from '@/services/api';

interface UseInterviewReturn {
  isRunning: boolean;
  isPaused: boolean;
  status: InterviewStatus['data'] | null;
  attentionHistory: AttentionHistoryResponse['data'] | null;
  attentionAnalysis: AttentionAnalysisResponse['data'] | null;
  startInterview: (position?: string) => Promise<void>;
  stopInterview: () => Promise<void>;
  pauseInterview: () => void;
  resumeInterview: () => void;
  fetchAttentionHistory: () => Promise<void>;
  fetchAttentionAnalysis: () => Promise<void>;
  error: string | null;
  isLoading: boolean;
}

export const useInterview = (): UseInterviewReturn => {
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [isPaused, setIsPaused] = useState<boolean>(false);
  const [status, setStatus] = useState<InterviewStatus['data'] | null>(null);
  const [attentionHistory, setAttentionHistory] = useState<AttentionHistoryResponse['data'] | null>(null);
  const [attentionAnalysis, setAttentionAnalysis] = useState<AttentionAnalysisResponse['data'] | null>(null);
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
      
      // 检查响应结构并正确提取数据
      if (response && typeof response === 'object') {
        // API返回的结构是 { data: {...}, is_running: boolean }
        // 由于axios响应拦截器已经返回了response.data，所以这里的response就是完整的InterviewStatus对象
        // 直接使用response.data和response.is_running
        const extractedData = response.data || {
          attention_score: 0,
          gaze_status: '未知',
          pose_status: '未知',
          gesture_status: '未知',
          face_detected: false,
          gaze_away_count: 0,
          pose_issue_count: 0,
          gesture_count: 0,
          session_time: 0,
          feedback: '系统运行中...'
        };
        
        console.log('提取的数据:', extractedData);
        console.log('is_running状态:', response.is_running);
        console.log('face_detected状态:', extractedData.face_detected);
        console.log('attention_score:', extractedData.attention_score);
        
        // 重要修复：不依赖后端的is_running状态，使用前端自己的状态管理
        // 只更新数据状态，不更新isRunning状态
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
      console.error('获取状态失败:', err);
      console.error('错误详情:', err instanceof Error ? err.message : '未知错误');
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
  }, []);

  // 开始面试
  const startInterview = useCallback(async (position?: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await api.startInterview(position);
      if (response.success) {
        // 重要修复：使用前端自己的状态管理，不依赖后端返回的is_running
        setIsRunning(true);
        // 立即获取一次状态
        await fetchStatus();
        // 然后开始定期获取状态
        intervalRef.current = setInterval(fetchStatus, 1000);
        console.log('面试已开始，定时器已启动');
      } else {
        // API返回失败，但仍视为面试已开始（前端状态优先）
        setIsRunning(true);
        setError(response.message || '开始面试失败');
        // 立即获取一次状态
        await fetchStatus();
        // 然后开始定期获取状态
        intervalRef.current = setInterval(fetchStatus, 1000);
        console.log('面试已开始(API返回失败)，定时器已启动');
      }
    } catch (err) {
      console.error('开始面试失败:', err);
      // API调用失败，但仍视为面试已开始（前端状态优先）
      setIsRunning(true);
      setError('开始面试失败，使用本地模拟模式');
      // 立即获取一次状态
      await fetchStatus();
      // 然后开始定期获取状态
      intervalRef.current = setInterval(fetchStatus, 1000);
      console.log('面试已开始(API调用失败)，定时器已启动');
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
        // 重要修复：使用前端自己的状态管理
        setIsRunning(false);
        // 停止定期获取状态
        clearStatusInterval();
        console.log('面试已停止，定时器已清除');
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

  // 暂停面试
  const pauseInterview = useCallback(() => {
    console.log('暂停面试');
    setIsPaused(true);
    if (intervalRef.current) {
      console.log('停止状态获取定时器');
      clearStatusInterval();
    }
  }, [clearStatusInterval]);

  // 获取注意力历史数据
  const fetchAttentionHistory = useCallback(async () => {
    try {
      const response = await api.getAttentionHistory();
      if (response.success) {
        setAttentionHistory(response.data);
      }
    } catch (err) {
      console.error('获取注意力历史数据失败:', err);
      setError('获取注意力历史数据失败');
    }
  }, []);

  // 获取注意力分析报告
  const fetchAttentionAnalysis = useCallback(async () => {
    try {
      const response = await api.getAttentionAnalysis();
      if (response.success) {
        setAttentionAnalysis(response.data);
      }
    } catch (err) {
      console.error('获取注意力分析报告失败:', err);
      setError('获取注意力分析报告失败');
    }
  }, []);

  // 恢复面试
  const resumeInterview = useCallback(() => {
    console.log('恢复面试');
    setIsPaused(false);
    if (isRunning && !intervalRef.current) {
      console.log('启动状态获取定时器');
      intervalRef.current = setInterval(fetchStatus, 1000);
    }
  }, [isRunning, fetchStatus, clearStatusInterval]);

  // 当面试状态改变时，更新定时器
  useEffect(() => {
    console.log('面试状态改变:', isRunning, '，暂停状态:', isPaused);
    if (isRunning && !isPaused && !intervalRef.current) {
      console.log('启动定时器，每秒获取状态');
      intervalRef.current = setInterval(fetchStatus, 1000);
    } else if ((!isRunning || isPaused) && intervalRef.current) {
      console.log('停止定时器');
      clearStatusInterval();
    }
    
    return () => {
      clearStatusInterval();
    };
  }, [isRunning, isPaused, fetchStatus, clearStatusInterval]);

  // 当面试停止时，自动获取注意力历史和分析报告
  useEffect(() => {
    if (!isRunning && !isPaused) {
      // 面试已停止，获取最终的注意力历史和分析报告
      fetchAttentionHistory();
      fetchAttentionAnalysis();
    }
  }, [isRunning, isPaused, fetchAttentionHistory, fetchAttentionAnalysis]);

  return {
    isRunning,
    isPaused,
    status,
    attentionHistory,
    attentionAnalysis,
    startInterview,
    stopInterview,
    pauseInterview,
    resumeInterview,
    fetchAttentionHistory,
    fetchAttentionAnalysis,
    error,
    isLoading,
  };
};