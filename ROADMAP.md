# 路线

## 远程仓库

- 仓库：https://github.com/1455224865w-cmd/OpenDevMate
- `main` 已推送初始提交 `9885451`。
- CI 工作流是 `.github/workflows/ci.yml`，只安装项目并运行 `pytest`。
- 首次推送的运行已成功：https://github.com/1455224865w-cmd/OpenDevMate/actions/runs/44689637795
- Milestone「0.2 下一步」跟踪下面三个 Issue：
  - #1 用 PostgreSQL 保存项目和任务
  - #2 只读同步 GitHub Issue
  - #3 外部 Agent 只在独立工作区执行
## 已完成：0.1.0

项目、任务拆分、状态机、执行记录、Diff、测试、审查、知识、目录扫描和仪表盘。

## 下一步

0.1.1 已完成的部分写在变更记录里。仍未完成的是需要真实数据库或仍未替换存储的部分。

1. 把存储换成 PostgreSQL，并保留现有测试所覆盖的规则。
2. 只读同步 GitHub Issue。不同步时不影响本地任务。
3. 接入一个外部 Agent 执行器。执行器必须在独立工作区运行，不能直接改默认分支。

## 暂不做

自动写代码、自动开 PR、多 Agent 调度和 Kubernetes。没有真实使用记录之前，这些只会增加运行面。

## 0.1.2

借鉴 [tickmarkr](https://github.com/alzahrani-khalid/tickmarkr) 的验收标准和 [LaneGate](https://github.com/sudheerdvn/lanegate) 的文件范围：任务可以声明验收条件和允许改动的路径。超出范围或测试仍失败时不能验收。没有这份约定时，原有审查流程不变。
