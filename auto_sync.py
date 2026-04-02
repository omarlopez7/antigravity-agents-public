"""
antigravity_sync.py — Sincronización Bidireccional GitHub <-> Local
=====================================================================
  - Detecta creaciones, modificaciones Y BORRADOS (on_deleted)
  - Hace git pull --rebase antes de cada push (evita conflictos)
  - Debounce de 2s para agrupar ráfagas de eventos del watcher
  - Logging real con rotación de archivo (no solo print)
  - Notificaciones desactivadas por defecto (ENABLE_NOTIFICATIONS)
  - Recuperación automática de commits pendientes sin subir
  - .gitignore creado automáticamente en el primer arranque
  - Modo --dry-run para probar sin tocar GitHub
"""

import os
import sys
import time
import socket
import logging
import argparse
import threading
import subprocess
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler

# --- NOTIFICACIONES (opcional: pip install win11toast) ---
try:
    from win11toast import toast as win_toast
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False

# --- WATCHDOG (pip install watchdog) ---
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ══════════════════════════════════════════════════════════════════════
#  CONFIGURACIÓN  (edita solo esta sección)
# ══════════════════════════════════════════════════════════════════════
REPO_URL             = "https://github.com/omarlopez7/antigravity-agents-public.git"
LOCAL_REPO_PATH      = Path(r"C:\src\antigravity-agents-public")
BRANCH               = "main"
PULL_INTERVAL        = 3     # segundos entre pulls automáticos
DEBOUNCE_SECS        = 2      # segundos de espera antes de subir cambios
ENABLE_NOTIFICATIONS = False  # Cambia a True si quieres notificaciones de Windows

LOG_FILE = LOCAL_REPO_PATH / "sync.log"

# Patrones ignorados al detectar cambios locales
IGNORE_PATTERNS = {
    ".git", "__pycache__", ".tmp", ".swp", ".DS_Store",
    "Thumbs.db", "*.pyc", "sync.log"
}

# ══════════════════════════════════════════════════════════════════════
#  LOGGER
# ══════════════════════════════════════════════════════════════════════
def build_logger() -> logging.Logger:
    logger = logging.getLogger("antigravity")
    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")

    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    try:
        fh = RotatingFileHandler(LOG_FILE, maxBytes=2_000_000, backupCount=3, encoding="utf-8")
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    except Exception:
        pass

    return logger

log = build_logger()

# ══════════════════════════════════════════════════════════════════════
#  UTILIDADES
# ══════════════════════════════════════════════════════════════════════
def notify(title: str, message: str):
    if ENABLE_NOTIFICATIONS and NOTIFICATIONS_AVAILABLE:
        try:
            win_toast(title, message)
        except Exception:
            pass
    log.info(f"[NOTIF] {title}: {message}")


def run_git(*args, capture=True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git"] + list(args),
        cwd=LOCAL_REPO_PATH,
        capture_output=capture,
        text=True
    )


def is_ignored(path: str) -> bool:
    p = Path(path)
    parts = set(p.parts)
    for pattern in IGNORE_PATTERNS:
        if pattern.startswith("*."):
            if p.suffix == pattern[1:]:
                return True
        elif pattern in parts or p.name == pattern:
            return True
    return False


def git_has_remote() -> bool:
    return "origin" in run_git("remote").stdout


def has_unpushed_commits() -> bool:
    result = run_git("rev-list", f"origin/{BRANCH}..HEAD", "--count")
    try:
        return int(result.stdout.strip()) > 0
    except ValueError:
        return False


def ensure_gitignore():
    gitignore = LOCAL_REPO_PATH / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text(
            "sync.log\n__pycache__/\n*.pyc\n.DS_Store\nThumbs.db\n*.tmp\n*.swp\n",
            encoding="utf-8"
        )
        log.info("📄 .gitignore creado automáticamente.")
        run_git("add", ".gitignore")
        run_git("commit", "-m", "chore: add .gitignore")

# ══════════════════════════════════════════════════════════════════════
#  SETUP DEL REPOSITORIO
# ══════════════════════════════════════════════════════════════════════
def setup_repo(dry_run: bool):
    LOCAL_REPO_PATH.mkdir(parents=True, exist_ok=True)
    log.info(f"📂 Directorio local: {LOCAL_REPO_PATH}")

    user_name   = os.getlogin()
    antigravity = Path(rf"C:\Users\{user_name}\.gemini\antigravity\.agents")
    if not antigravity.exists():
        if not dry_run:
            try:
                subprocess.run(
                    ["cmd", "/c", "mklink", "/D", str(antigravity), str(LOCAL_REPO_PATH)],
                    check=True
                )
                log.info(f"🔗 Symlink creado: {antigravity} -> {LOCAL_REPO_PATH}")
            except subprocess.CalledProcessError:
                log.error("❌ Symlink falló — ejecuta como Administrador la primera vez.")
        else:
            log.info(f"[DRY-RUN] Crearía symlink: {antigravity}")

    if not (LOCAL_REPO_PATH / ".git").exists():
        if not dry_run:
            run_git("init")
            run_git("remote", "add", "origin", REPO_URL)
            run_git("branch", "-M", BRANCH)
            log.info("🟪 Repositorio Git inicializado.")
        else:
            log.info("[DRY-RUN] Inicializaría repo git.")
    elif not git_has_remote():
        run_git("remote", "add", "origin", REPO_URL)

    if dry_run:
        return

    ensure_gitignore()
    pull_from_github(force=True)

    if has_unpushed_commits():
        log.info("🔄 Commits pendientes detectados al iniciar — subiendo...")
        for intento in range(1, 4):
            result = run_git("push", "origin", BRANCH)
            if result.returncode == 0:
                log.info("⬆️  Commits pendientes subidos correctamente.")
                break
            log.warning(f"Push pendiente intento {intento}/3 falló, reintentando en 5s…")
            time.sleep(5)

# ══════════════════════════════════════════════════════════════════════
#  OPERACIONES PRINCIPALES
# ══════════════════════════════════════════════════════════════════════
_push_lock = threading.Lock()


def pull_from_github(force: bool = False) -> bool:
    hora   = datetime.now().strftime("%H:%M:%S")
    result = run_git("pull", "origin", BRANCH, "--rebase", "--autostash")
    salida = (result.stdout + result.stderr).lower()

    if result.returncode != 0:
        log.error(f"🟥 [{hora}] Pull falló:\n{result.stderr.strip()}")
        notify("Antigravity Sync", f"⚠️ Pull falló a las {hora}")
        return False

    up_to_date = "already up to date" in salida or "actualizado" in salida
    if not up_to_date or force:
        log.info(f"⬇️  [{hora}] Cambios DESCARGADOS de GitHub")
        if not up_to_date:
            notify("Antigravity Sync", f"⬇️ Nuevos cambios descargados ({hora})")
        return True
    return False


def push_to_github(reason: str = "cambio local", dry_run: bool = False) -> bool:
    with _push_lock:
        hora      = datetime.now().strftime("%H:%M:%S")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        computer  = socket.gethostname()

        run_git("add", "-A")
        status = run_git("status", "--porcelain")

        if not status.stdout.strip():
            log.debug(f"[{hora}] Sin cambios locales que subir.")
            return False

        if dry_run:
            log.info(f"[DRY-RUN] [{hora}] Subiría:\n{status.stdout.strip()}")
            return True

        pull_result = run_git("pull", "origin", BRANCH, "--rebase", "--autostash")
        if pull_result.returncode != 0:
            log.error(f"🟥 [{hora}] Pull pre-push falló.\n{pull_result.stderr}")
            notify("Antigravity Sync", "⚠️ Conflicto detectado — revisa el repositorio")
            return False

        mensaje = f"Auto-sync [{computer}]: {timestamp} — {reason}"
        commit_result = run_git("commit", "-m", mensaje)
        if commit_result.returncode != 0:
            log.debug(f"[{hora}] Commit vacío o ya resuelto.")
            return False

        for intento in range(1, 4):
            push_result = run_git("push", "origin", BRANCH)
            if push_result.returncode == 0:
                log.info(f"⬆️  [{hora}] Cambios SUBIDOS a GitHub ({reason})")
                notify("Antigravity Sync", f"⬆️ Cambios subidos ({hora})")
                return True
            log.warning(f"🟨 Push intento {intento}/3 falló. Reintentando en 5s…")
            time.sleep(5)

        log.error(f"🟥 [{hora}] Push falló después de 3 intentos.")
        notify("Antigravity Sync", f"❌ Push falló a las {hora}")
        return False

# ══════════════════════════════════════════════════════════════════════
#  WATCHER CON DEBOUNCE
# ══════════════════════════════════════════════════════════════════════
class SincronizadorLocal(FileSystemEventHandler):

    def __init__(self, dry_run: bool):
        super().__init__()
        self.dry_run     = dry_run
        self._timer      = None
        self._lock       = threading.Lock()
        self._last_event = ""

    def _schedule_push(self, reason: str):
        with self._lock:
            self._last_event = reason
            if self._timer is not None:
                self._timer.cancel()
            self._timer = threading.Timer(
                DEBOUNCE_SECS,
                lambda: push_to_github(self._last_event, self.dry_run)
            )
            self._timer.start()

    def on_created(self, event):
        if not event.is_directory and not is_ignored(event.src_path):
            self._schedule_push(f"archivo creado: {Path(event.src_path).name}")

    def on_modified(self, event):
        if not event.is_directory and not is_ignored(event.src_path):
            self._schedule_push(f"archivo modificado: {Path(event.src_path).name}")

    def on_deleted(self, event):
        if not event.is_directory and not is_ignored(event.src_path):
            self._schedule_push(f"archivo BORRADO: {Path(event.src_path).name}")

    def on_moved(self, event):
        if not event.is_directory and not is_ignored(event.dest_path):
            nombre = f"{Path(event.src_path).name} -> {Path(event.dest_path).name}"
            self._schedule_push(f"archivo renombrado: {nombre}")

# ══════════════════════════════════════════════════════════════════════
#  BUCLE PERIÓDICO DE PULL
# ══════════════════════════════════════════════════════════════════════
def pull_loop(dry_run: bool):
    while True:
        time.sleep(PULL_INTERVAL)
        if dry_run:
            continue
        pull_from_github()
        if has_unpushed_commits():
            log.warning("🔄 Commits sin subir detectados — reintentando push…")
            push_to_github("reintento automático de commits pendientes")

# ══════════════════════════════════════════════════════════════════════
#  PUNTO DE ENTRADA
# ══════════════════════════════════════════════════════════════════════
def main():
    parser = argparse.ArgumentParser(description="Antigravity Sync — GitHub <-> Local")
    parser.add_argument("--dry-run", action="store_true", help="Simula sin ejecutar git push/pull reales")
    args = parser.parse_args()

    dry_run = args.dry_run
    if dry_run:
        log.info("🧪 MODO DRY-RUN: ningún cambio real será enviado a GitHub")

    setup_repo(dry_run)

    handler  = SincronizadorLocal(dry_run)
    observer = Observer()
    observer.schedule(handler, str(LOCAL_REPO_PATH), recursive=True)
    observer.start()

    pull_thread = threading.Thread(target=pull_loop, args=(dry_run,), daemon=True)
    pull_thread.start()

    log.info("=" * 54)
    log.info(" 🚀 ANTIGRAVITY SYNC ACTIVO")
    log.info(f" 📂 Local:  {LOCAL_REPO_PATH}")
    log.info(f" 🌐 Remoto: {REPO_URL} ({BRANCH})")
    log.info(f" ⏱  Pull cada {PULL_INTERVAL}s | Debounce {DEBOUNCE_SECS}s")
    log.info("=" * 54)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log.info("\n🛑 Deteniendo Antigravity Sync…")
        observer.stop()

    observer.join()
    log.info("✅ Sistema detenido correctamente.")


if __name__ == "__main__":
    main()