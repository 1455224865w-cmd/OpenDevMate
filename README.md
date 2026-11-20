# OpenDevMate

OpenDevMate 帮助人管理 AI Coding Agent 的工作，不替代 Agent 写代码。

人负责需求和验收。系统保存项目知识、任务状态、Diff、测试记录和审查结论。当前版本不会调用外部模型，也不会自动改仓库。

## 0.1.0 能做什么

- 建立项目和任务，并把一个任务拆成子任务。
- 任务状态只允许 `draft → ready → running → review → accepted`，也可以进入 `blocked`。
- 按项目知识生成一份可复制给 Agent 的任务说明。
- 记录执行结果、Diff、测试数量和审查结论。高风险审查不能直接验收。
- 扫描允许目录内的文件类型和顶层模块，拒绝目录之外的路径。
- 提供 `/api/dashboard` 和 `/dashboard`。

## 现在不做什么

- 不连接真实 Coding Agent。
- 不同步 GitHub Issue 或 PR。
- 不使用 Java 21。原因见 `docs/decisions/0001-mvp-stack.md`。

## 本地运行

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
pytest
uvicorn opendevmate.api:app --reload
```

打开 `http://127.0.0.1:8000/docs`。数据库默认是当前目录的 `opendevmate.sqlite3`。扫描根目录受 `OPENDEVMATE_WORKSPACE` 限制，默认是进程工作目录。

## 许可证

Apache-2.0。选择理由见架构决策记录。
