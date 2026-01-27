// src/hooks/use-voice.ts - 语音合成Hook
import { useState, useCallback, useRef } from 'react';

interface UseVoiceReturn {
  speak: (text: string) => Promise<void>;
  stopSpeaking: () => void;
  isSpeaking: boolean;
  error: string | null;
}

export const useVoice = (): UseVoiceReturn => {
  const [isSpeaking, setIsSpeaking] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const currentUtteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

  // 停止当前语音播放
  const stopSpeaking = useCallback(() => {
    if ('speechSynthesis' in window) {
      // 停止所有正在播放的语音
      speechSynthesis.cancel();
      console.log('已停止当前语音播放');
    }
  }, []);

  // 语音合成函数 - 使用浏览器的Web Speech API
  const speak = useCallback(async (text: string): Promise<void> => {
    console.log('开始语音播报:', text);
    
    // 停止当前正在播放的语音
    stopSpeaking();
    
    setIsSpeaking(true);
    setError(null);

    try {
      // 检查浏览器是否支持Web Speech API
      if ('speechSynthesis' in window) {
        console.log('使用浏览器的Web Speech API进行语音合成');
        
        // 创建一个新的语音实例
        const utterance = new SpeechSynthesisUtterance(text);
        
        // 设置语音属性
        utterance.lang = 'zh-CN'; // 使用中文语音
        utterance.rate = 1; // 语速
        utterance.pitch = 1; // 音调
        utterance.volume = 1; // 音量
        
        // 保存当前语音实例
        currentUtteranceRef.current = utterance;
        
        // 播放语音
        speechSynthesis.speak(utterance);
        
        // 等待语音播放完成
        await new Promise<void>((resolve) => {
          utterance.onend = () => {
            console.log('语音播报完成');
            resolve();
          };
          utterance.onerror = (event) => {
            console.error('语音播放错误:', event);
            resolve();
          };
        });
      } else {
        console.error('浏览器不支持Web Speech API');
        throw new Error('浏览器不支持语音合成功能');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '语音合成异常';
      setError(errorMessage);
      console.error('语音合成错误:', errorMessage);
      console.error('详细错误:', err);
    } finally {
      setIsSpeaking(false);
    }
  }, [stopSpeaking]);

  return {
    speak,
    stopSpeaking,
    isSpeaking,
    error,
  };
};
