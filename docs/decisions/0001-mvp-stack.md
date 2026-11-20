# 0001 使用 Python 和 SQLite

初稿希望使用 Java 21、Spring Boot 和 PostgreSQL。当前开发环境没有可用 JDK，Maven 也无法编译。五个项目需要同一套能在 GitHub Actions 里跑完的测试。

因此 0.1.0 使用 Python 3.12、FastAPI 和 SQLite。业务规则放在 `service.py`，不放在路由里。如果以后要换成 Java，先移植状态机和扫描规则，再换 Web 框架。

不引入消息队列、微服务或 Kubernetes。一个进程足够保存任务记录。

许可证使用 Apache-2.0。它允许使用和修改，并带有专利授权条款，适合长期协作的开发工具。GPL 会迫使衍生作品开源，对这类工具过重。这是维护者的选择，不是法律意见。
