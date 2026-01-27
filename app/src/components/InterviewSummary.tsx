import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity, CheckCircle, AlertCircle, BookOpen, Clock, RefreshCw } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { AttentionAnalysis } from "@/services/api";

interface InterviewSummaryProps {
  interviewPosition: string;
  sessionTime: number;
  attentionAnalysis: AttentionAnalysis | null;
  error?: string | null;
  onRetry?: () => void;
  isLoading?: boolean;
  videoSaved?: boolean;
  videoSaveError?: string | null;
}

export default function InterviewSummary({ interviewPosition, sessionTime, attentionAnalysis, error, onRetry, isLoading, videoSaved, videoSaveError }: InterviewSummaryProps) {
  // 格式化时间
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}分${secs}秒`;
  };

  // 获取评分等级
  const getScoreLevel = (score: number) => {
    if (score >= 90) return { text: "优秀", color: "bg-green-100 text-green-800" };
    if (score >= 80) return { text: "良好", color: "bg-blue-100 text-blue-800" };
    if (score >= 70) return { text: "中等", color: "bg-yellow-100 text-yellow-800" };
    if (score >= 60) return { text: "及格", color: "bg-orange-100 text-orange-800" };
    return { text: "需要改进", color: "bg-red-100 text-red-800" };
  };

  // 显示错误信息 - 优先显示错误，无论其他状态如何
  if (error) {
    return (
      <Card className="w-full max-w-3xl mx-auto mt-8">
        <CardHeader>
          <CardTitle className="text-2xl font-bold">面试总结</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <AlertCircle className="mx-auto h-16 w-16 text-red-500 mb-4" />
            <p className="text-red-600 font-medium mb-2">生成面试总结时出错</p>
            <p className="text-gray-600 mb-4">{error}</p>
            {onRetry && (
              <Button onClick={onRetry} variant="outline" className="mt-4">
                <RefreshCw className="mr-2 h-4 w-4" />
                重新获取
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    );
  }

  // 显示加载状态 - 只有当没有错误时才显示
  if (!attentionAnalysis) {
    return (
      <Card className="w-full max-w-3xl mx-auto mt-8">
        <CardHeader>
          <CardTitle className="text-2xl font-bold">面试总结</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <Activity className="mx-auto h-16 w-16 text-blue-500 mb-4 animate-pulse" />
            <p className="text-gray-600">正在生成面试总结...</p>
            <p className="text-gray-400 text-sm mt-2">请稍候</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const { attention_score, scoring_criteria, recommendations, attention_states, statistics } = attentionAnalysis;
  const scoreLevel = getScoreLevel(attention_score);

  // 计算注意力状态百分比
  const totalStates = attention_states.high + attention_states.medium + attention_states.low;
  const highPercent = totalStates > 0 ? (attention_states.high / totalStates) * 100 : 0;
  const mediumPercent = totalStates > 0 ? (attention_states.medium / totalStates) * 100 : 0;
  const lowPercent = totalStates > 0 ? (attention_states.low / totalStates) * 100 : 0;

  return (
    <Card className="w-full max-w-3xl mx-auto mt-8">
      <CardHeader>
        <div className="flex justify-between items-start">
          <CardTitle className="text-2xl font-bold">面试总结</CardTitle>
          <Badge className={scoreLevel.color} variant="secondary">
            {scoreLevel.text}
          </Badge>
        </div>
        <p className="text-sm text-gray-500 mt-1">
          {interviewPosition} 岗位 - 面试时长: {formatTime(sessionTime)}
        </p>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* 注意力评分 */}
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold">注意力评分</h3>
            <span className="text-2xl font-bold">{Math.round(attention_score)}</span>
          </div>
          <Progress value={attention_score} className="h-3" />
        </div>

        {/* 注意力状态分布 */}
        <div>
          <h3 className="text-lg font-semibold mb-3">注意力状态分布</h3>
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm">高度集中</span>
              <span className="text-sm font-medium">{Math.round(highPercent)}%</span>
            </div>
            <Progress value={highPercent} className="h-2 bg-gray-200" />
            
            <div className="flex justify-between items-center">
              <span className="text-sm">中等集中</span>
              <span className="text-sm font-medium">{Math.round(mediumPercent)}%</span>
            </div>
            <Progress value={mediumPercent} className="h-2 bg-gray-200" />
            
            <div className="flex justify-between items-center">
              <span className="text-sm">注意力分散</span>
              <span className="text-sm font-medium">{Math.round(lowPercent)}%</span>
            </div>
            <Progress value={lowPercent} className="h-2 bg-gray-200" />
          </div>
        </div>

        {/* 评分依据 */}
        <div>
          <h3 className="text-lg font-semibold mb-3">评分依据</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {Object.entries(scoring_criteria).map(([key, criteria]) => (
              <div key={key} className="bg-gray-50 p-3 rounded-lg">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-sm font-medium">{criteria.description}</span>
                  <span className="text-xs text-gray-500">{Math.round(criteria.weight * 100)}%</span>
                </div>
                <span className="text-xs">{criteria.current_status}</span>
              </div>
            ))}
          </div>
        </div>

        {/* 表现亮点 */}
        <div>
          <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
            <CheckCircle className="h-5 w-5 text-green-500" />
            表现亮点
          </h3>
          <ul className="space-y-2">
            {attention_score >= 85 && (
              <li className="flex items-start gap-2">
                <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                <span className="text-sm">注意力表现优秀，保持了良好的专注度</span>
              </li>
            )}
            {statistics.gaze_away_count < 5 && (
              <li className="flex items-start gap-2">
                <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                <span className="text-sm">视线保持稳定，很少看向其他地方</span>
              </li>
            )}
            {statistics.pose_issue_count < 5 && (
              <li className="flex items-start gap-2">
                <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                <span className="text-sm">保持了良好的坐姿，姿态规范</span>
              </li>
            )}
            {statistics.gesture_count < 5 && (
              <li className="flex items-start gap-2">
                <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                <span className="text-sm">小动作较少，保持了专业形象</span>
              </li>
            )}
            {statistics.gaze_away_count >= 5 && statistics.pose_issue_count >= 5 && statistics.gesture_count >= 5 && (
              <li className="flex items-start gap-2">
                <AlertCircle className="h-4 w-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                <span className="text-sm">虽然各方面表现有待提升，但坚持完成了面试</span>
              </li>
            )}
          </ul>
        </div>

        {/* 改进建议 */}
        <div>
          <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-yellow-500" />
            改进建议
          </h3>
          <ul className="space-y-2">
            {recommendations.map((recommendation, index) => (
              <li key={index} className="flex items-start gap-2">
                <AlertCircle className="h-4 w-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                <span className="text-sm">{recommendation}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* 视频保存状态 */}
        <div className={`p-4 rounded-lg ${videoSaved === true ? 'bg-green-50' : videoSaveError ? 'bg-red-50' : 'bg-gray-50'}`}>
          <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
            {videoSaved === true ? (
              <CheckCircle className="h-5 w-5 text-green-600" />
            ) : videoSaveError ? (
              <AlertCircle className="h-5 w-5 text-red-600" />
            ) : (
              <Activity className="h-5 w-5 text-gray-600" />
            )}
            视频保存状态
          </h3>
          {videoSaved === true ? (
            <p className="text-sm text-green-700">
              面试视频已成功保存到项目文件夹。您可以在项目目录中查看录制的视频文件。
            </p>
          ) : videoSaveError ? (
            <p className="text-sm text-red-700">
              视频保存失败: {videoSaveError}
            </p>
          ) : (
            <p className="text-sm text-gray-700">
              视频正在保存中，请稍候...
            </p>
          )}
        </div>

        {/* 学习资源 */}
        <div className="bg-blue-50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
            <BookOpen className="h-5 w-5 text-blue-600" />
            学习资源推荐
          </h3>
          <p className="text-sm text-gray-700">
            建议您继续学习面试技巧和注意力管理方法，提高面试表现。
            可以通过练习冥想、模拟面试等方式提升专注力和表达能力。
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
