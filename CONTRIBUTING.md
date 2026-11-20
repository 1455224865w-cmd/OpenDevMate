# 参与 OpenDevMate

1. 先看 README 和 `docs/decisions/`，不要另起一套目标。
2. 一个改动只解决一个使用场景。
3. 运行 `pytest`。没有测试结果就不要说功能已经完成。
4. 不要提交 `.env`、Token、数据库口令或客户数据。
5. 不确定的结论要标明证据，不能写成事实。
6. Pull Request 使用仓库里的模板。

本地安装：

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
pytest
```
