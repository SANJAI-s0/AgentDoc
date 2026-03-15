from __future__ import annotations

import socket
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = ROOT / ".env"

REQUIRED_KEYS = [
    "DJANGO_SECRET_KEY",
    "MONGODB_URI",
    "MINIO_ENDPOINT",
    "MINIO_ACCESS_KEY",
    "MINIO_SECRET_KEY",
    "MINIO_BUCKET",
    "GEMINI_API_KEY",
    "AGENT_INTERNAL_TOKEN",
]


def load_env(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def check_port(host: str, port: int, timeout: float = 1.5) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((host, port))
        return True
    except Exception:
        return False
    finally:
        sock.close()


def status_line(ok: bool, label: str, detail: str = "") -> str:
    mark = "PASS" if ok else "FAIL"
    return f"[{mark}] {label}{' - ' + detail if detail else ''}"


def main() -> int:
    print("AgentDoc Local Preflight")
    print("=" * 26)

    env = load_env(ENV_PATH)
    score = {"pass": 0, "fail": 0}

    def record(ok: bool, label: str, detail: str = "") -> None:
        print(status_line(ok, label, detail))
        if ok:
            score["pass"] += 1
        else:
            score["fail"] += 1

    record((ROOT / "backend" / "manage.py").exists(), "Backend project layout")
    record((ROOT / "frontend" / "package.json").exists(), "Frontend project layout")
    record(ENV_PATH.exists(), ".env file present", str(ENV_PATH))

    placeholders = {"change-me", "replace-with-your-gemini-api-key", "replace-with-random-long-token"}
    for key in REQUIRED_KEYS:
        value = env.get(key, "")
        ok = bool(value) and value not in placeholders
        record(ok, f"Env key: {key}")

    mongodb_up = check_port("127.0.0.1", 27017)
    minio_up = check_port("127.0.0.1", 9000)
    backend_up = check_port("127.0.0.1", 8000)
    frontend_up = check_port("127.0.0.1", 5173)

    record(mongodb_up, "MongoDB reachable", "127.0.0.1:27017")
    record(minio_up, "MinIO reachable", "127.0.0.1:9000")
    record(backend_up, "Backend reachable", "127.0.0.1:8000")
    record(frontend_up, "Frontend reachable", "127.0.0.1:5173")

    sample_dir = ROOT / "sample"
    record(sample_dir.exists(), "Sample corpus available", str(sample_dir))

    print("-" * 26)
    print(f"Summary: {score['pass']} passed, {score['fail']} failed")
    print("Tip: run this before demos and deployments to catch setup issues early.")

    return 0 if score["fail"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
