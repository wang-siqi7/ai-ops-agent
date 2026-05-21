# SuperBizAgent

> 企业级智能对话和运维助手，支持 RAG 知识库问答和 AIOps 智能诊断

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-latest-orange.svg)](https://www.langchain.com/)
[![Milvus](https://img.shields.io/badge/Milvus-Lite-yellow.svg)](https://milvus.io/)

## ✨ 核心特性

- 🤖 **智能对话** - LangChain 多轮对话 + 流式输出
- 📚 **RAG 问答** - 向量检索增强，支持文档上传、自动建立向量索引、自动更新知识库
- 🔧 **AIOps 诊断** - Plan-Execute-Replan 自动故障诊断和根因分析
- 🌐 **Web 界面** - 现代化 UI，支持多种对话模式：快速问答/流式对话
- 🔌 **MCP 集成** - 日志查询和监控数据工具接入
- 🐳 **双模式支持** - 支持 Milvus Lite（无需Docker）和 Milvus Server（Docker）两种模式

## 🛠️ 技术栈

- **框架**: FastAPI + LangChain + LangGraph
- **LLM**: 阿里云 DashScope (通义千问)
- **向量库**: Milvus (支持 Lite 嵌入式模式，无需 Docker)
- **工具协议**: MCP (Model Context Protocol)

## 🚀 快速开始（无需 Docker！）

本项目支持 **Milvus Lite 模式**，可以直接在 Windows 上运行，无需安装 Docker。

### 环境要求

- Python 3.11+
- 阿里云 DashScope API Key ([获取地址](https://dashscope.aliyun.com/))

### Windows 环境（推荐）

#### 方式一：使用启动脚本（最简单）

```powershell
# 1. 克隆项目
git clone <repository_url>
cd super_biz_agent_py

# 2. 双击运行或命令行运行
.\start-windows.bat
```

#### 方式二：手动安装

```powershell
# 1. 克隆项目
git clone <repository_url>
cd super_biz_agent_py

# 2. 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 复制并编辑配置文件
copy .env.example .env
# 编辑 .env 文件，填入 DASHSCOPE_API_KEY

# 5. 启动 MCP 服务（在新窗口中）
python mcp_servers/cls_server.py
python mcp_servers/monitor_server.py

# 6. 启动 FastAPI 服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 9900
```

### Linux/macOS 环境

```bash
# 1. 克隆项目
git clone <repository_url>
cd super_biz_agent_py

# 2. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 复制并编辑配置文件
cp .env.example .env
vim .env  # 填入 DASHSCOPE_API_KEY

# 5. 启动服务
make init
```

### 访问服务

- **Web 界面**: http://localhost:9900
- **API 文档**: http://localhost:9900/docs

---

## 🐳 使用 Docker 运行 Milvus Server（可选）

如果你需要处理大量数据或需要完整的 Milvus 功能，可以使用 Docker 运行 Milvus Server：

### Windows

```powershell
# 使用 Docker 模式启动
start-windows.bat
# 脚本会检测 Docker 状态，如未运行则自动切换到 Milvus Lite 模式
```

### Linux/macOS

```bash
# 使用 Milvus Server 模式
make init-server
# 或
make up    # 启动 Milvus Docker
make start # 启动服务
```

---

## 📁 项目结构

```
super_biz_agent_py/
├── app/                                    # 应用核心
│   ├── __init__.py                         # 包初始化
│   ├── main.py                             # FastAPI 应用入口
│   ├── config.py                           # 配置管理（环境变量、MCP 服务器配置）
│   ├── api/                                # API 路由层
│   ├── services/                           # 业务服务层
│   ├── agent/                              # Agent 模块
│   ├── models/                             # 数据模型层
│   ├── tools/                              # Agent 工具集
│   ├── core/                               # 核心组件（Milvus 客户端）
│   └── utils/                              # 工具类
├── mcp_servers/                            # MCP 服务器
│   ├── cls_server.py                       # CLS 日志查询服务
│   └── monitor_server.py                   # 监控数据服务
├── aiops-docs/                             # 运维知识库
├── static/                                 # Web 前端
├── .env.example                            # 环境变量模板
├── requirements.txt                        # Python 依赖
├── pyproject.toml                          # 项目配置
└── README.md                               # 项目说明
```

## ⚙️ 配置说明

通过 `.env` 文件配置：

```bash
# 阿里云LLM DashScope 配置（必填）
DASHSCOPE_API_KEY=your-api-key
DASHSCOPE_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
DASHSCOPE_MODEL=qwen-max

# Milvus 配置
# 使用 Milvus Lite（默认本地文件，无需 Docker）
MILVUS_URI=./milvus_lite.db

# 或者使用 Milvus Server（需要 Docker）
# MILVUS_HOST=localhost
# MILVUS_PORT=19530

# RAG 配置
RAG_TOP_K=3
CHUNK_MAX_SIZE=800
CHUNK_OVERLAP=100
```

## 🎯 AIOps 智能运维

基于 **Plan-Execute-Replan** 模式实现自动故障诊断。

### 诊断流程
```
1. Planner 制定计划 → 生成 4-6 个诊断步骤
2. Executor 执行步骤 → 调用 MCP 工具（日志查询、监控数据）
3. Replanner 评估结果 → 决定继续/调整/生成报告
4. 输出诊断报告 → 根因分析 + 运维建议
```

## 🐛 常见问题

### 1. 端口被占用

```powershell
# Windows
netstat -ano | findstr :9900
taskkill /F /PID <PID>

# Linux/macOS
lsof -i :9900
kill -9 <PID>
```

### 2. 依赖安装失败

```bash
# 确保 Python 版本 >= 3.11
python --version

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3. Milvus 连接失败

```bash
# 检查 .env 配置
cat .env | grep MILVUS

# Milvus Lite 模式下，数据文件默认在 ./milvus_lite.db
# 删除后可重新创建（数据会丢失）
rm milvus_lite.db
```

### 4. API Key 错误

```bash
# 检查环境变量
# Windows
type .env | findstr DASHSCOPE_API_KEY

# Linux/macOS
grep DASHSCOPE_API_KEY .env
```

## 📝 开发指南

### 常用命令

```bash
# 项目管理
make init              # 一键初始化（Milvus Lite）
make start            # 启动所有服务
make stop             # 停止所有服务
make restart          # 重启所有服务
make check            # 检查服务状态

# 文档管理
make upload           # 上传文档到向量库
make list-docs        # 列出可上传的文档

# 代码质量
make format           # 格式化代码
make lint             # 代码检查
make test             # 运行测试
```

### Windows 批处理命令

```powershell
# 启动服务
.\start-windows.bat

# 停止服务
.\stop-windows.bat
```

## 📚 参考资源

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [LangChain 文档](https://python.langchain.com/)
- [LangGraph Plan-Execute](https://langchain-ai.github.io/langgraph/tutorials/plan-and-execute/)
- [阿里云 DashScope](https://dashscope.aliyun.com/)
- [Milvus Lite 文档](https://milvus.io/docs/overview.md)
- [MCP 协议](https://modelcontextprotocol.io/)

## 📄 许可证

MIT License
