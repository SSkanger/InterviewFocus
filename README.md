# 智能面试模拟系统

这是一个基于人工智能的面试模拟系统，可以实时分析面试者的面部表情、视线方向、头部姿态和小动作，并提供智能反馈。

## 系统架构

- **后端**: Python + Flask + OpenCV + MediaPipe
- **前端**: React + TypeScript + Tailwind CSS + Vite

## 功能特点

1. **实时视频分析**: 通过摄像头捕捉面试者的面部表情和姿态
2. **智能反馈**: 基于AI分析提供实时反馈和建议
3. **注意力评分**: 实时计算面试者的注意力分数
4. **多维度检测**: 面部检测、视线方向、头部姿态、小动作检测
5. **友好界面**: 现代化的Web界面，支持实时视频流显示

## 安装与运行

### 前置要求

- Python 3.8+
- Node.js 16+
- 摄像头设备

### 安装步骤

1. **创建Python虚拟环境**:
   
   #### Windows系统:
   ```powershell
   # 在项目根目录下创建虚拟环境
   python -m venv p_envs
   
   # 激活虚拟环境
   p_envs\Scripts\activate
   ```
   
   #### Linux/MacOS系统:
   ```bash
   # 在项目根目录下创建虚拟环境
   python3 -m venv p_envs
   
   # 激活虚拟环境
   source p_envs/bin/activate
   ```

2. **安装Python依赖**:
   ```
   cd src
   pip install -r requirements.txt
   ```

3. **安装前端依赖**:
   ```
   cd app
   npm install
   ```

### 运行系统

#### 方法一: 使用启动脚本 (推荐)

在项目根目录下运行:
```
# Windows
start.bat

# Linux/MacOS
# 需要创建一个类似的启动脚本或手动启动
```

#### 方法二: 手动启动

1. **启动后端服务器**:
   ```
   # Windows
   p_envs\Scripts\python.exe src\web_server.py
   
   # Linux/MacOS
   p_envs/bin/python src/web_server.py
   ```

2. **启动前端服务器 (新终端)**:
   ```
   cd app
   npm run dev
   ```

3. 打开浏览器访问: http://localhost:5173

## 使用说明

1. 点击"开始面试"按钮启动系统
2. 系统会自动连接摄像头并开始分析
3. 右侧面板会显示实时状态和注意力评分
4. 系统会根据分析结果提供智能反馈
5. 点击"停止面试"结束会话

## 技术实现

### 后端技术栈
- Flask: Web框架
- OpenCV: 图像处理
- MediaPipe: 面部和姿态检测
- threading: 多线程处理

### 前端技术栈
- React: UI框架
- TypeScript: 类型安全
- Tailwind CSS: 样式框架
- Axios: HTTP客户端
- Lucide React: 图标库

## API接口

- `GET /api/status`: 获取系统状态
- `POST /api/start`: 启动面试
- `POST /api/stop`: 停止面试
- `GET /video_feed`: 获取视频流

## 注意事项

1. 确保摄像头权限已开启
2. 使用Chrome或Edge浏览器以获得最佳体验
3. 保持良好的光线条件以提高检测准确性
4. 首次运行可能需要下载模型文件，请耐心等待

## 故障排除

1. 如果摄像头无法打开，请检查摄像头权限
2. 如果页面无法加载，请确认前后端服务都已启动
3. 如果视频流显示异常，请刷新页面重试