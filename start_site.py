import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
REQ = BASE_DIR / "requirements.txt"
URL = "http://127.0.0.1:5000"


def ensure_requirements() -> None:
    """Install requirements if Flask is missing."""
    try:
        import flask  # noqa: F401
        return
    except Exception:
        pass

    if not REQ.exists():
        raise FileNotFoundError("requirements.txt not found рядом с start_site.py")

    print("[INFO] Устанавливаю зависимости... Это может занять пару минут.")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(REQ)])


def main() -> None:
    ensure_requirements()

    env = os.environ.copy()
    env["HOST"] = "127.0.0.1"
    env["PORT"] = "5000"

    print("[INFO] Запускаю сайт...")
    proc = subprocess.Popen([sys.executable, "webapp.py"], cwd=BASE_DIR, env=env)

    try:
        time.sleep(1.2)
        webbrowser.open(URL)
        print(f"[INFO] Сайт открыт: {URL}")
        print("[INFO] Чтобы остановить сервер, закройте это окно или нажмите Ctrl+C.")
        proc.wait()
    except KeyboardInterrupt:
        print("\n[INFO] Останавливаю сервер...")
    finally:
        if proc.poll() is None:
            proc.terminate()


if __name__ == "__main__":
    main()
