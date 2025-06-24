# Ploughman AI - 智能数据分析与可视化平台

Ploughman AI是一个基于多代理架构的智能数据分析与可视化系统，能够帮助用户快速分析数据、生成洞察并以直观的图表形式展示结果。

## 主要功能

- **自然语言数据分析**：通过自然语言描述数据需求，系统自动完成数据查询与分析
- **智能数据可视化**：根据数据特点自动生成合适的图表类型
- **多源数据整合**：支持从多种数据源（数据库、文件等）获取数据
- **任务自动化**：复杂任务自动分解为多个子任务并协调完成

## 技术架构

Ploughman AI采用多代理架构，主要模块包括：

- **调度代理**：负责分析用户请求并协调其他代理完成任务
- **数据采集代理**：从互联网或文件中获取数据
- **数据库代理**：与各类数据库交互，执行查询和写入操作
- **可视化代理**：将数据转化为直观的图表
- **工具服务**：提供底层功能支持（通过FastMCP实现）

## 环境准备

1. 克隆项目仓库：
```bash
   git clone https://github.com/yourusername/ploughmanai.git
  cd ploughmanai
```

2. 安装Python依赖：
```bash
pip install -r requirements.txt
```

3. 启动MCP工具服务：
```bash
python mcp_tools.py
```

4. 启动Gradio前端：
```bash
python app.py
```

5. 访问界面：
```bash
在浏览器打开 http://localhost:7860
```

## 使用示例
1. **简单查询**：
- 输入：分析sales_data表中的销售趋势
- 系统：返回销售数据的趋势分析和图表

2. **跨源分析**：
- 输入：分析数据库中的用户行为数据并与上周进行对比
- 系统：从数据库获取数据，进行对比分析并生成对比图表

3. **复杂任务**：
- 输入：收集人工智能领域的最新发展数据并生成可视化报告
- 系统：自动分解任务 -> 网络数据采集 -> 数据库存储 -> 数据分析 -> 结果可视化

## 部署到Docker

1. 构建镜像：
```bash
docker build -t ploughmanai .
```

2. 运行容器：
```bash
docker run -p 7860:7860 ploughmanai
```

3. 访问服务：
在浏览器打开 http://localhost:7860
复制

## 开发者文档

### 项目结构
```bash
PloughmanAI/
├── app.py             # Gradio前端界面程序
├── agents/             # 多代理模块目录
│   ├── scheduler_agent.py  # 任务调度代理
│   ├── data_agent.py   # 数据采集代理
│   ├── db_agent.py     # 数据库管理代理
│   └── viz_agent.py    # 可视化代理
├── mcp_tools.py        # FastMCP工具服务定义
├── data/               # 数据存储目录
│   └── ploughmanai.db  # SQLite数据库文件
├── Dockerfile          # Docker容器配置文件
├── requirements.txt    # Python依赖文件
└── README.md           # 项目说明文档
```

### 扩展功能

要添加新功能，可以：

1. 在`agents/`目录下创建新的代理模块
2. 在`mcp_tools.py`中注册新的工具函数
3. 更新调度代理的指令说明

## 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. git仓库
2. 创建新分支：`git checkout -b feature-xxx`
3. 提交更改：`git commit -m "Add some feature"`
4. 推送分支：`git push origin feature-xxx`
5. 提交Pull Request

## 联系我们

有问题或建议请联系：contact@ploughmanai.com