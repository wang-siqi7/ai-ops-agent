# AI Ops Agent

基于 LangGraph 的智能运维诊断 Agent，通过 Plan-Execute-Replan 实现多步推理，集成 MCP 工具调用与 RAG 知识库，实现告警自动诊断与根因分析。

## 技术栈

- **Agent框架**: LangChain + LangGraph
- **设计模式**: ReAct、Plan-Execute-Replan
- **工具集成**: MCP协议（日志查询、监控数据）
- **知识库**: RAG + ChromaDB（两阶段检索）
- **后端**: FastAPI + SSE

## 核心能力

### 1. 多 Agent 协同架构

通过 LangGraph 编排三个 Agent 协同工作：

| Agent | 职责 |
|-------|------|
| RAG 知识库 Agent | 文档解析、向量检索、知识问答 |
| ReAct 对话 Agent | 日常咨询、多轮对话、上下文记忆 |
| Plan-Execute-Replan 运维 Agent | 告警诊断、多步推理、工具调用 |

### 2. Plan-Execute-Replan 诊断流程

- **Plan**: 将故障诊断任务拆解为多步计划
- **Execute**: 逐步执行计划，调用 MCP 工具
- **Replan**: 评估结果，决定继续或生成报告

### 3. RAG 知识库优化

- 多类型文档自动解析与向量化入库
- 两阶段检索：向量检索 + 重排序
- 查询改写、意图路由与拒答机制，减少无效回答

### 4. 对话记忆管理

- 分层记忆机制：保留最近多轮原文
- 当 Token 达上下文窗口 70% 时，自动触发 LLM 摘要压缩
- 保证长会话连贯性与上下文自动加载

### 5. MCP 工具集成

- 通过 MCP 协议统一接入日志服务（CLS）和监控服务（Monitor）
- 实现自动化告警查询与日志分析
- 支持工具调用重试与指数退避

### 6. SSE 流式输出

- 实时返回 Agent 决策过程
- 用户可看到“步骤规划→工具调用→结果分析→生成建议”
