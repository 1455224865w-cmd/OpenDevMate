# 开发

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
pytest
```

Docker 镜像只启动 API，不包含 PostgreSQL。`docker compose up` 前需要本机 Docker。当前测试不依赖容器。

环境变量：

- `OPENDEVMATE_DB`：SQLite 文件路径。
- `OPENDEVMATE_WORKSPACE`：允许扫描的根目录。
