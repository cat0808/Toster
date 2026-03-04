"""Создаёт чистую папку PortableSite без .git и лишних служебных файлов."""

from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "PortableSite"

KEEP_FILES = {
    "webapp.py",
    "start_site.py",
    "run_site.bat",
    "run_site.sh",
    "requirements.txt",
    "README.md",
    "wsgi.py",
    "passenger_wsgi.py",
}
KEEP_DIRS = {"static", "templates", "media"}

if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True)

for name in KEEP_FILES:
    src = ROOT / name
    if src.exists():
        shutil.copy2(src, OUT / name)

for name in KEEP_DIRS:
    src = ROOT / name
    dst = OUT / name
    if src.exists() and src.is_dir():
        shutil.copytree(src, dst)

print(f"Готово: {OUT}")
