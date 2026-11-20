"""运行配置。设置了 NACOS_SERVER 时以 Nacos 为准，否则使用环境变量。"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request

DEFAULTS = {'host': '0.0.0.0', 'port': 8000, 'database': '/data/opendevmate.sqlite3', 'default_locale': 'zh', 'workspace': '/data/workspace'}
DATA_ID = "opendevmate.properties"


class ConfigError(RuntimeError):
    """配置无法读取。"""


def load_settings(environ: dict | None = None) -> dict:
    env = os.environ if environ is None else environ
    settings = {
        "host": env.get("APP_HOST", DEFAULTS["host"]),
        "port": int(env.get("APP_PORT", DEFAULTS["port"])),
        "database": env.get("APP_DATABASE", DEFAULTS["database"]),
        "default_locale": env.get("APP_LOCALE", DEFAULTS["default_locale"]),
        "config_source": "environment",
    }
    if "workspace" in DEFAULTS:
        settings["workspace"] = env.get("APP_WORKSPACE", DEFAULTS["workspace"])
    server = env.get("NACOS_SERVER", "").strip()
    if not server:
        return settings
    payload = _fetch_nacos(server, env)
    remote = parse_config_text(payload)
    for key in ("host", "port", "database", "workspace", "default_locale"):
        if key not in settings or key not in remote:
            continue
        value = remote[key]
        if isinstance(value, str) and "${" in value:
            continue
        if key == "port":
            settings[key] = int(value)
        else:
            settings[key] = value
    settings["config_source"] = "nacos"
    return settings


def parse_config_text(text: str) -> dict:
    stripped = text.strip()
    if not stripped:
        return {}
    if stripped[0] in "{[":
        loaded = json.loads(stripped)
        flat = _flatten(loaded) if isinstance(loaded, dict) else {}
    else:
        lines = [line.strip() for line in stripped.splitlines() if line.strip() and not line.strip().startswith("#")]
        equals = sum("=" in line for line in lines)
        colons = sum(":" in line and "=" not in line for line in lines)
        flat = {}
        for line in lines:
            if equals >= colons:
                if "=" not in line:
                    continue
                key, value = line.split("=", 1)
            else:
                if ":" not in line:
                    continue
                key, value = line.split(":", 1)
            flat[key.strip()] = value.strip().strip("'\"")
    return _normalize(flat)


def _flatten(data: dict, prefix: str = "") -> dict:
    flat = {}
    for key, value in data.items():
        name = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(value, dict):
            flat.update(_flatten(value, name))
        else:
            flat[name] = value
    return flat


def _normalize(flat: dict) -> dict:
    aliases = {
        "host": "host",
        "app.host": "host",
        "APP_HOST": "host",
        "port": "port",
        "app.port": "port",
        "APP_PORT": "port",
        "database": "database",
        "app.database": "database",
        "APP_DATABASE": "database",
        "workspace": "workspace",
        "app.workspace": "workspace",
        "APP_WORKSPACE": "workspace",
        "default_locale": "default_locale",
        "app.default-locale": "default_locale",
        "app.default_locale": "default_locale",
        "APP_LOCALE": "default_locale",
    }
    found = {}
    for key, value in flat.items():
        target = aliases.get(key)
        if target:
            found[target] = value
    return found


def _fetch_nacos(server: str, env: dict) -> str:
    base = server.rstrip("/")
    if not base.startswith("http://") and not base.startswith("https://"):
        base = "http://" + base
    token = _login(base, env.get("NACOS_USERNAME", ""), env.get("NACOS_PASSWORD", ""))
    query = {
        "dataId": env.get("NACOS_DATA_ID", "").strip() or DATA_ID,
        "group": env.get("NACOS_GROUP", "").strip() or "DEFAULT_GROUP",
        "tenant": env.get("NACOS_NAMESPACE", "").strip(),
    }
    if token:
        query["accessToken"] = token
    url = base + "/nacos/v1/cs/configs?" + urllib.parse.urlencode(query)
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raise ConfigError(f"Nacos 配置读取失败，HTTP {exc.code}") from None
    except urllib.error.URLError:
        raise ConfigError("Nacos 配置服务不可达") from None


def _login(base: str, username: str, password: str) -> str:
    if not username:
        return ""
    body = urllib.parse.urlencode({"username": username, "password": password}).encode("utf-8")
    request = urllib.request.Request(base + "/nacos/v1/auth/login", data=body)
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise ConfigError(f"Nacos 登录失败，HTTP {exc.code}") from None
    except urllib.error.URLError:
        raise ConfigError("Nacos 配置服务不可达") from None
    token = payload.get("accessToken") if isinstance(payload, dict) else ""
    if not token:
        raise ConfigError("Nacos 登录没有返回访问令牌")
    return str(token)
