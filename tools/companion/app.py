#!/usr/bin/env python3
"""Local-only sidecar for a user-provided Star Cyber Lab and GoClaw service."""
from __future__ import annotations

import hmac
import json
import os
import re
import secrets
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
MAX_REQUEST_BYTES = 64 * 1024
MAX_RESPONSE_BYTES = 256 * 1024
LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}
ASSETS = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/styles.css": ("styles.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/scene.js": ("scene.js", "text/javascript; charset=utf-8"),
    "/favicon.svg": ("favicon.svg", "image/svg+xml"),
}


def load_env_file(path: Path) -> None:
    """Read KEY=value without interpreting the file as shell code."""
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip()
        if not re.fullmatch(r"[A-Z][A-Z0-9_]*", key):
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ.setdefault(key, value)


def local_url(value: str, *, base: bool = False) -> str:
    """Reject credentials, public destinations, fragments and query strings."""
    try:
        parsed = urllib.parse.urlsplit(value)
        port = parsed.port
    except ValueError as exc:
        raise ValueError("invalid address") from exc
    if (parsed.scheme not in {"http", "https"} or parsed.hostname not in LOCAL_HOSTS
            or parsed.username is not None or parsed.password is not None
            or parsed.query or parsed.fragment or (port is not None and not 1 <= port <= 65535)):
        raise ValueError("address must be a local http(s) URL without credentials")
    if base and parsed.path not in {"", "/"}:
        raise ValueError("GoClaw URL must be the origin, without an API path")
    return value.rstrip("/") if base else value


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


OPENER = urllib.request.build_opener(NoRedirect, urllib.request.ProxyHandler({}))


def read_response(req: urllib.request.Request, timeout: float) -> bytes:
    with OPENER.open(req, timeout=timeout) as response:
        body = response.read(MAX_RESPONSE_BYTES + 1)
        if len(body) > MAX_RESPONSE_BYTES:
            raise ValueError("response too large")
        return body


def check_health(url: str) -> dict:
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"}, method="GET")
        read_response(req, timeout=2.5)
        return {"state": "online", "description": "نقطة الصحة المضبوطة تستجيب"}
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            return {"state": "auth", "description": "نقطة الصحة تستجيب وتتطلب مصادقة"}
        return {"state": "unavailable", "description": "الخدمة لم تؤكد الجاهزية"}
    except (OSError, ValueError, urllib.error.URLError):
        return {"state": "unavailable", "description": "تعذّر الاتصال بالخدمة"}


def read_audit_summary(path: Path) -> dict:
    """Return counts only from a local report; never send file names to a provider."""
    try:
        if path.stat().st_size > 8 * 1024 * 1024:
            return {"state": "invalid", "description": "التقرير أكبر من 8MB"}
        payload = json.loads(path.read_text(encoding="utf-8"))
        files = payload.get("files") if isinstance(payload, dict) else None
        if not isinstance(files, list) or len(files) > 3000:
            raise ValueError("invalid audit report")
        valid = [item for item in files if isinstance(item, dict)]
        paths = {value for item in valid for value in (item.get("api_paths") if isinstance(item.get("api_paths"), list) else []) if isinstance(value, str)}
        flags = sum(len(item.get("flags")) for item in valid if isinstance(item.get("flags"), list))
        return {"state": "available", "files": sum(item.get("classification") == "JS_SOURCE" for item in valid),
                "api_paths": len(paths), "flags": flags}
    except FileNotFoundError:
        return {"state": "missing", "description": "لم يُعثر على تقرير محلي"}
    except (OSError, ValueError, UnicodeError, json.JSONDecodeError):
        return {"state": "invalid", "description": "تعذر قراءة التقرير المحلي"}


def build_config() -> dict:
    load_env_file(ROOT / ".env")
    port = int(os.environ.get("STAR_COMPANION_PORT", "8055"))
    if not 1 <= port <= 65535:
        raise ValueError("STAR_COMPANION_PORT must be a valid port")
    base = local_url(os.environ.get("GOCLAW_BASE_URL", "http://127.0.0.1:18790"), base=True)
    lab_value = os.environ.get("STAR_LAB_HEALTH_URL", "").strip()
    lab = local_url(lab_value) if lab_value else None
    agent = os.environ.get("GOCLAW_AGENT_ID", "default").strip()
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", agent):
        raise ValueError("GOCLAW_AGENT_ID has invalid characters")
    report_value = os.environ.get("STAR_AUDIT_REPORT", "").strip()
    report = Path(report_value).expanduser() if report_value else ROOT.parent.parent / "reports" / "analysis.json"
    return {"port": port, "goclaw_url": base, "lab_url": lab, "agent": agent,
            "report_path": report,
            "token": os.environ.get("GOCLAW_GATEWAY_TOKEN", "").strip(),
            "csrf": secrets.token_urlsafe(32)}


def normalize_messages(value) -> list[dict]:
    if not isinstance(value, list) or not 1 <= len(value) <= 20:
        raise ValueError("invalid messages")
    messages = []
    for item in value:
        if not isinstance(item, dict) or item.get("role") not in {"user", "assistant"}:
            raise ValueError("invalid role")
        content = item.get("content")
        if not isinstance(content, str) or not 1 <= len(content.strip()) <= 6000:
            raise ValueError("invalid content")
        messages.append({"role": item["role"], "content": content.strip()})
    if messages[-1]["role"] != "user":
        raise ValueError("last message must be from the user")
    return messages


def ask_goclaw(config: dict, messages: list[dict]) -> str:
    payload = json.dumps({"model": "goclaw:" + config["agent"], "messages": messages,
                          "stream": False}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(config["goclaw_url"] + "/v1/chat/completions", data=payload,
        headers={"Authorization": "Bearer " + config["token"], "Content-Type": "application/json",
                 "Accept": "application/json"}, method="POST")
    data = json.loads(read_response(req, timeout=90).decode("utf-8"))
    result = data["choices"][0]["message"]["content"]
    if not isinstance(result, str) or not result.strip():
        raise ValueError("empty assistant response")
    return result.strip()


def make_handler(config: dict):
    class Handler(BaseHTTPRequestHandler):
        server_version = "StarCompanion/1.0"
        sys_version = ""

        def log_message(self, _format, *_args):
            # Message contents, tokens and upstream failures never go into access logs.
            return

        def allow_host(self):
            try:
                host = self.headers.get("Host", "")
                parsed = urllib.parse.urlsplit("http://" + host)
                return (parsed.hostname in LOCAL_HOSTS and parsed.port == config["port"]
                        and parsed.username is None and parsed.password is None
                        and parsed.path == "" and not parsed.query and not parsed.fragment)
            except ValueError:
                return False

        def headers_common(self, kind, length, code=200):
            self.send_response(code)
            self.send_header("Content-Type", kind)
            self.send_header("Content-Length", str(length))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy", "default-src 'self'; img-src 'self' data:; "
                             "script-src 'self'; style-src 'self'; connect-src 'self'; base-uri 'none'; "
                             "frame-ancestors 'none'; form-action 'self'")
            self.end_headers()

        def send_json(self, obj, code=200):
            data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
            self.headers_common("application/json; charset=utf-8", len(data), code)
            self.wfile.write(data)

        def do_GET(self):
            if not self.allow_host():
                return self.send_json({"error": "invalid host"}, 403)
            path = urllib.parse.urlsplit(self.path).path
            if path == "/api/session":
                return self.send_json({"csrf": config["csrf"], "agent": config["agent"],
                                       "chat_configured": bool(config["token"])})
            if path == "/api/status":
                return self.send_json({"checked_at": datetime.now(timezone.utc).isoformat(),
                    "lab": check_health(config["lab_url"]) if config["lab_url"] else
                           {"state": "not_configured", "description": "لم يُحدد عنوان نقطة صحة المختبر"},
                    "goclaw": check_health(config["goclaw_url"] + "/health"),
                    "report": read_audit_summary(config["report_path"]),
                    "chat_configured": bool(config["token"])})
            if path not in ASSETS:
                return self.send_json({"error": "not found"}, 404)
            filename, kind = ASSETS[path]
            content = (STATIC / filename).read_bytes()
            self.headers_common(kind, len(content))
            self.wfile.write(content)

        def do_POST(self):
            if not self.allow_host():
                return self.send_json({"error": "invalid host"}, 403)
            if urllib.parse.urlsplit(self.path).path != "/api/chat":
                return self.send_json({"error": "not found"}, 404)
            origin = self.headers.get("Origin")
            if origin and origin != "http://" + self.headers.get("Host", ""):
                return self.send_json({"error": "invalid origin"}, 403)
            if not hmac.compare_digest(self.headers.get("X-Star-CSRF", ""), config["csrf"]):
                return self.send_json({"error": "invalid session"}, 403)
            if self.headers.get_content_type() != "application/json":
                return self.send_json({"error": "content type required"}, 415)
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                return self.send_json({"error": "invalid request"}, 400)
            if not 0 < length <= MAX_REQUEST_BYTES:
                return self.send_json({"error": "invalid request size"}, 413)
            if not config["token"]:
                return self.send_json({"error": "لم يُضبط رمز GoClaw بعد. راجع ملف الإعدادات."}, 503)
            try:
                body = json.loads(self.rfile.read(length).decode("utf-8"))
                messages = normalize_messages(body.get("messages") if isinstance(body, dict) else None)
            except (ValueError, UnicodeError, json.JSONDecodeError):
                return self.send_json({"error": "تحقق من الرسالة ثم حاول مجدداً."}, 400)
            try:
                response = ask_goclaw(config, messages)
                return self.send_json({"reply": response})
            except urllib.error.HTTPError as exc:
                if exc.code in (401, 403):
                    return self.send_json({"error": "رفض GoClaw بيانات الوصول أو صلاحية الوكيل."}, 502)
                return self.send_json({"error": "تعذرت معالجة الطلب في GoClaw."}, 502)
            except (OSError, ValueError, KeyError, IndexError, TypeError, json.JSONDecodeError):
                return self.send_json({"error": "تعذر الاتصال بـGoClaw أو قراءة رده."}, 502)

    return Handler


def main():
    try:
        config = build_config()
        server = ThreadingHTTPServer(("127.0.0.1", config["port"]), make_handler(config))
    except (ValueError, OSError) as exc:
        print("تعذر التشغيل:", exc, file=sys.stderr)
        return 1
    print(f"Star Cyber Lab Companion: http://127.0.0.1:{config['port']}", flush=True)
    print("Local access only. Stop with Ctrl+C.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
