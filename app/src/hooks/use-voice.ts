// src/hooks/use-voice.ts - 语音合成Hook
import { useState, useCallback } from 'react';

interface UseVoiceReturn {
  speak: (text: string) => Promise<void>;
  isSpeaking: boolean;
  error: string | null;
}

export const useVoice = (): UseVoiceReturn => {
  const [isSpeaking, setIsSpeaking] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // 语音合成函数 - 使用浏览器内置的Web Speech API
  const speak = useCallback(async (text: string): Promise<void> => {
    console.log('开始语音播报:', text);
    setIsSpeaking(true);
    setError(null);

    try {
      // 检查浏览器是否支持语音合成
      if ('speechSynthesis' in window) {
        // 使用浏览器内置的语音合成API
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'zh-CN';
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;

        // 创建一个Promise来等待语音合成完成
        await new Promise<void>((resolve, reject) => {
          utterance.onend = () => resolve();
          utterance.onerror = (event) => reject(new Error(`语音合成错误: ${event.error}`));
          speechSynthesis.speak(utterance);
        });
        console.log('语音播报完成');
      } else {
        // 如果浏览器不支持语音合成，调用后端API
        console.log('浏览器不支持语音合成，调用后端API');
        const response = await fetch('http://127.0.0.1:5000/api/questions/ask', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            question: text,
            position: '通用',
          }),
        });

        const data = await response.json();
        if (!data.success) {
          throw new Error(data.message || '语音合成失败');
        }
        console.log('后端语音API调用成功');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '语音合成异常';
      setError(errorMessage);
      console.error('语音合成错误:', errorMessage);
      console.error('详细错误:', err);
    } finally {
      setIsSpeaking(false);
    }
  }, []);

  return {
    speak,
    isSpeaking,
    error,
  };
};
