"""容器入口。先读 Nacos 或环境变量，再启动服务。"""

from __future__ import annotations

import os
from pathlib import Path

import uvicorn

from opendevmate.api import create_app
from opendevmate.service import Store
from opendevmate.settings import load_settings


def main() -> None:
    settings = load_settings()
    os.environ["APP_LOCALE"] = settings["default_locale"]
    database = Path(settings["database"])
    database.parent.mkdir(parents=True, exist_ok=True)
    workspace = Path(settings["workspace"])
    workspace.mkdir(parents=True, exist_ok=True)
    Path("/tmp/app.port").write_text(str(settings["port"]), encoding="utf-8")
    app = create_app(Store(str(database)), workspace)
    uvicorn.run(app, host=settings["host"], port=int(settings["port"]))


if __name__ == "__main__":
    main()
