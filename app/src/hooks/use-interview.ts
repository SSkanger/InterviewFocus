// src/hooks/use-interview.ts - 面试状态管理Hook
import { useState, useEffect, useCallback, useRef } from 'react';
import { api, InterviewStatus, AttentionHistoryResponse, AttentionAnalysisResponse, AttentionAnalysis } from '@/services/api';

interface UseInterviewReturn {
  isRunning: boolean;
  isPaused: boolean;
  status: InterviewStatus['data'] | null;
  attentionHistory: AttentionHistoryResponse['data'] | null;
  attentionAnalysis: AttentionAnalysis | null;
  startInterview: (position?: string) => Promise<void>;
  stopInterview: () => Promise<void>;
  pauseInterview: () => void;
  resumeInterview: () => void;
  fetchAttentionHistory: () => Promise<void>;
  fetchAttentionAnalysis: () => Promise<void>;
  resetInterview: () => void;
  error: string | null;
  isLoading: boolean;
}

export const useInterview = (): UseInterviewReturn => {
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [isPaused, setIsPaused] = useState<boolean>(false);
  const [status, setStatus] = useState<InterviewStatus['data'] | null>(null);
  const [attentionHistory, setAttentionHistory] = useState<AttentionHistoryResponse['data'] | null>(null);
  const [attentionAnalysis, setAttentionAnalysis] = useState<AttentionAnalysis | null>(null);
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
        // 只有当面试正在运行时，才清除错误信息
        // 面试停止后，保留错误信息
        if (isRunning) {
          setError(null);
        }
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
  }, [isRunning]);

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
      console.log('开始获取注意力历史数据...');
      const response = await api.getAttentionHistory();
      console.log('获取注意力历史响应:', response);
      
      if (response && response.success) {
        console.log('获取注意力历史成功，数据:', response.data);
        setAttentionHistory(response.data);
        return true;
      } else {
        console.error('获取注意力历史失败，响应:', response);
        setError('获取注意力历史数据失败：' + (response?.message || '未知错误'));
        return false;
      }
    } catch (err) {
      console.error('获取注意力历史数据失败:', err);
      setError('获取注意力历史数据失败');
      return false;
    }
  }, []);

  // 获取注意力分析报告
  const fetchAttentionAnalysis = useCallback(async () => {
    try {
      console.log('开始获取注意力分析报告...');
      
      // 使用现有的api方法
      const response = await api.getAttentionAnalysis();
      
      console.log('获取注意力分析响应:', response);
      
      // 检查响应格式
      if (response && typeof response === 'object') {
        console.log('响应包含success字段:', 'success' in response);
        console.log('success字段值:', response.success);
        
        if (response.success) {
          console.log('获取注意力分析成功，数据:', response.data);
          setAttentionAnalysis(response.data);
          return true;
        } else {
          console.error('获取注意力分析失败，响应:', response);
          setError('获取注意力分析报告失败：' + (response.message || '未知错误'));
          // 错误时不要重置attentionAnalysis，保持原有数据
          return false;
        }
      } else {
        console.error('获取注意力分析失败，响应格式不正确:', response);
        setError('获取注意力分析报告失败：响应格式不正确');
        // 错误时不要重置attentionAnalysis，保持原有数据
        return false;
      }
    } catch (err) {
      console.error('获取注意力分析报告失败:', err);
      console.error('错误类型:', err instanceof Error ? err.name : '未知类型');
      console.error('错误信息:', err instanceof Error ? err.message : '未知错误');
      
      setError('获取注意力分析报告失败：' + (err instanceof Error ? err.message : '未知错误'));
      // 错误时不要重置attentionAnalysis，保持原有数据
      return false;
    }
  }, []);

  // 重置面试状态
  const resetInterview = useCallback(() => {
    setIsRunning(false);
    setIsPaused(false);
    setStatus(null);
    setAttentionHistory(null);
    setAttentionAnalysis(null);
    setError(null);
    // 清除定时器
    clearStatusInterval();
  }, [clearStatusInterval]);

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

  // 添加一个标志位，确保总结只获取一次
  const summaryFetchedRef = useRef(false);
  
  // 当面试停止时，自动获取注意力历史和分析报告
  useEffect(() => {
    // 只在面试停止且未获取过总结时执行一次
    if (!isRunning && !isPaused && !summaryFetchedRef.current) {
      const fetchInterviewSummary = async () => {
        // 标记为已获取，避免重复调用
        summaryFetchedRef.current = true;
        
        console.log('面试已停止，开始获取最终总结数据...');
        
        // 添加延迟，确保后端有足够时间处理和保存数据
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        try {
          // 先获取注意力历史数据
          console.log('开始获取注意力历史数据...');
          await fetchAttentionHistory();
          
          // 然后获取注意力分析报告
          console.log('开始获取注意力分析报告...');
          const success = await fetchAttentionAnalysis();
          
          if (success) {
            console.log('获取面试总结完成');
          } else {
            console.log('获取面试总结失败');
          }
        } catch (error) {
          console.error('获取面试总结时发生异常:', error);
        }
      };
      
      fetchInterviewSummary();
    }
    
    // 重置标志位，当面试重新开始时
    if (isRunning) {
      summaryFetchedRef.current = false;
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
    resetInterview,
    error,
    isLoading,
  };
};