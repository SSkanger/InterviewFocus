import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { api } from '@/services/api';

const VoiceTest: React.FC = () => {
  const [message, setMessage] = useState<string>('');
  const [position, setPosition] = useState<string>('Python开发工程师');
  const [status, setStatus] = useState<string>('就绪');
  
  // 直接测试语音API
  const testVoiceApi = async () => {
    setStatus('正在测试语音API...');
    try {
      const response = await fetch('http://127.0.0.1:5000/api/questions/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: message || '这是一个直接的语音测试，不经过任何封装',
          position,
        }),
      });
      
      const data = await response.json();
      if (data.success) {
        setStatus('语音API测试成功');
      } else {
        setStatus(`语音API测试失败: ${data.message}`);
      }
    } catch (error) {
      setStatus(`语音API测试异常: ${error instanceof Error ? error.message : '未知错误'}`);
    }
  };
  
  // 测试开始面试API
  const testStartInterview = async () => {
    setStatus('正在测试开始面试API...');
    try {
      const response = await api.startInterview(position);
      if (response.success) {
        setStatus('开始面试API测试成功');
      } else {
        setStatus(`开始面试API测试失败: ${response.message}`);
      }
    } catch (error) {
      setStatus(`开始面试API测试异常: ${error instanceof Error ? error.message : '未知错误'}`);
    }
  };
  
  // 测试停止面试API
  const testStopInterview = async () => {
    setStatus('正在测试停止面试API...');
    try {
      const response = await api.stopInterview();
      if (response.success) {
        setStatus('停止面试API测试成功');
      } else {
        setStatus(`停止面试API测试失败: ${response.message}`);
      }
    } catch (error) {
      setStatus(`停止面试API测试异常: ${error instanceof Error ? error.message : '未知错误'}`);
    }
  };
  
  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>语音功能测试</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label htmlFor="position" className="text-sm font-medium">面试岗位</label>
            <Select value={position} onValueChange={setPosition}>
              <SelectTrigger id="position">
                <SelectValue placeholder="请选择面试岗位" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Python开发工程师">Python开发工程师</SelectItem>
                <SelectItem value="产品经理">产品经理</SelectItem>
                <SelectItem value="护士">护士</SelectItem>
                <SelectItem value="小学教师">小学教师</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <div className="space-y-2">
            <label htmlFor="message" className="text-sm font-medium">测试消息</label>
            <Input
              id="message"
              placeholder="请输入测试消息"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
            />
          </div>
          
          <div className="space-y-2">
            <label className="text-sm font-medium">测试状态</label>
            <div className="p-2 bg-muted rounded-md">{status}</div>
          </div>
          
          <div className="grid grid-cols-2 gap-2">
            <Button onClick={testVoiceApi} className="w-full">
              测试语音API
            </Button>
            <Button onClick={testStartInterview} className="w-full">
              测试开始面试
            </Button>
            <Button onClick={testStopInterview} className="w-full">
              测试停止面试
            </Button>
            <Button 
              onClick={() => {
                window.location.href = '/';
              }}
              variant="outline" 
              className="w-full"
            >
              返回主页面
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default VoiceTest;