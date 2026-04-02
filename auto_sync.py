import os
import time
import socket
import subprocess
import urllib.request
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from win11toast import toast

# --- CONFIGURACIÓN ---
REPO_URL = "https://github.com/omarlopez7/antigravity-agents-public.git"
LOCAL_REPO_PATH = r"C:\src\antigravity-agents-public"
USER_NAME = os.getlogin()
ANTIGRAVITY_PATH = rf"C:\Users\{USER_NAME}\.gemini\antigravity\.agents"
ICON_PATH = r"C:\src\github_icon.png"

# --- 1. PREPARACIÓN DE CARPETAS ---
os.makedirs(r"C:\src", exist_ok=True)
if not os.path.exists(LOCAL_REPO_PATH):
    os.makedirs(LOCAL_REPO_PATH, exist_ok=True)
    print(f"🟦 Carpeta creada en {LOCAL_REPO_PATH}")

# Descarga de icono para la notificación
if not os.path.exists(ICON_PATH):
    try:
        urllib.request.urlretrieve("https://cdn-icons-png.flaticon.com/512/25/25231.png", ICON_PATH)
    except: pass

# --- 2. VÍNCULO CON ANTIGRAVITY (SYMLINK) ---
if not os.path.exists(ANTIGRAVITY_PATH):
    print("🟨 Creando enlace simbólico...")
    # Se ejecuta via CMD para asegurar compatibilidad de mklink
    subprocess.run(["cmd", "/c", f'mklink /D "{ANTIGRAVITY_PATH}" "{LOCAL_REPO_PATH}"'], shell=True)

# --- 3. INICIALIZACIÓN DE GIT ---
os.chdir(LOCAL_REPO_PATH)
if not os.path.exists(".git"):
    subprocess.run(["git", "init"])
    subprocess.run(["git", "remote", "add", "origin", REPO_URL])
    print("🟪 Repositorio Git inicializado.")

# --- 4. FUNCIÓN DE SINCRONIZACIÓN MAESTRA ---
def sync_now(direction):
    hora = datetime.now().strftime('%H:%M:%S')
    fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    pc_name = socket.gethostname()

    try:
        os.chdir(LOCAL_REPO_PATH)
        if direction == "UP":
            # Subir cambios
            subprocess.run(["git", "add", "."], capture_output=True)
            # Solo hacemos commit si hay cambios reales para evitar errores
            status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
            if status.stdout.strip():
                msg = f"Auto-sync: {fecha} de {pc_name}"
                subprocess.run(["git", "commit", "-m", msg], capture_output=True)
                subprocess.run(["git", "push", "origin", "main"], capture_output=True)
                print(f"🟩 >>> [{hora}] Cambios SUBIDOS a GitHub")
                toast("🚀 Respaldo Exitoso", f"Cambios subidos a las {hora}", icon=ICON_PATH, app_id="AntigravitySync")
        
        else:
            # Descargar cambios (DOWN)
            res = subprocess.run(["git", "pull", "origin", "main", "--rebase"], capture_output=True, text=True)
            # Solo notifica si Git dice que realmente descargó algo
            if "Already up to date" not in res.stdout and "actualizado" not in res.stdout.lower():
                print(f"⬜ --- [{hora}] Cambios DESCARGADOS de GitHub")
                toast("📥 Nuevos Agentes", f"Actualizado desde la nube a las {hora}", icon=ICON_PATH, on_click=LOCAL_REPO_PATH, app_id="AntigravitySync")
    
    except Exception as e:
        print(f"🟥 Error en la sincronización: {e}")

# --- 5. MONITOR DE CAMBIOS (WATCHER) ---
class WatcherHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory and ".git" not in event.src_path:
            sync_now("UP")
    def on_created(self, event):
        if not event.is_directory and ".git" not in event.src_path:
            sync_now("UP")

# --- 6. EJECUCIÓN ---
if __name__ == "__main__":
    print("==============================================")
    print(" SISTEMA DE AGENTES ANTIGRAVITY ACTIVO (PY) ")
    print(f" Repositorio: {LOCAL_REPO_PATH}")
    print("==============================================")

    # Iniciar el Watcher (Equivalente al Register-ObjectEvent de PS)
    observer = Observer()
    observer.schedule(WatcherHandler(), LOCAL_REPO_PATH, recursive=True)
    observer.start()

    # Bucle de descarga (Equivalente al while($true) de PS)
    try:
        while True:
            sync_now("DOWN")
            time.sleep(60) # Pausa de 60 segundos
    except KeyboardInterrupt:
        observer.stop()
    observer.join()