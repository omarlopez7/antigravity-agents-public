import os
import time
import socket
import subprocess
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from win11toast import toast  # <--- NOTIFICACIONES

# --- CONFIGURACIÓN ---
REPO_URL = "https://github.com/omarlopez7/antigravity-agents-public.git"
LOCAL_REPO_PATH = r"C:\src\antigravity-agents-public"
USER_NAME = os.getlogin()
ANTIGRAVITY_PATH = rf"C:\Users\{USER_NAME}\.gemini\antigravity\.agents"
BRANCH = "main"

# --- 1. PREPARACIÓN DE CARPETAS ---
if not os.path.exists(r"C:\src"):
    os.makedirs(r"C:\src")

if not os.path.exists(LOCAL_REPO_PATH):
    os.makedirs(LOCAL_REPO_PATH)
    print(f"🟦 Carpeta creada en {LOCAL_REPO_PATH}")

# --- 2. VÍNCULO CON ANTIGRAVITY (SYMLINK) ---
if not os.path.exists(ANTIGRAVITY_PATH):
    print("🟨 Creando enlace simbólico para Antigravity...")
    try:
        subprocess.run(["cmd", "/c", "mklink", "/D", ANTIGRAVITY_PATH, LOCAL_REPO_PATH], check=True)
    except subprocess.CalledProcessError:
        print("❌ Error: Debes ejecutar este script como Administrador la primera vez.")

# --- 3. INICIALIZACIÓN DE GIT ---
os.chdir(LOCAL_REPO_PATH)
if not os.path.exists(os.path.join(LOCAL_REPO_PATH, ".git")):
    subprocess.run(["git", "init"])
    subprocess.run(["git", "remote", "add", "origin", REPO_URL])
    subprocess.run(["git", "branch", "-M", BRANCH])
    print("🟪 Repositorio Git inicializado.")

# --- 4. FUNCIÓN DE SINCRONIZACIÓN MAESTRA ---
def sync_now(direction):
    hora_actual = datetime.now().strftime('%H:%M:%S')
    fecha_completa = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
    computer_name = socket.gethostname()

    try:
        os.chdir(LOCAL_REPO_PATH)
        if direction == "UP":
            subprocess.run(["git", "add", "."], capture_output=True)
            status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
            
            if status.stdout.strip():
                mensaje = f"Auto-sync: {fecha_completa} de {computer_name}"
                subprocess.run(["git", "commit", "-m", mensaje], capture_output=True)
                subprocess.run(["git", "push", "origin", BRANCH], capture_output=True)
                print(f"🟩 >>> [{hora_actual}] Cambios SUBIDOS a GitHub")
        
        elif direction == "DOWN":
            resultado = subprocess.run(["git", "pull", "origin", BRANCH, "--rebase"], capture_output=True, text=True)
            salida_git = resultado.stdout.lower() + resultado.stderr.lower()
            
            # Si Git NO dice que ya está actualizado, significa que descargó algo nuevo
            if "already up to date" not in salida_git and "actualizado" not in salida_git:
                print(f"⬜ --- [{hora_actual}] Cambios DESCARGADOS de GitHub")
                
                # --- NOTIFICACIÓN DE WINDOWS ---
                try:
                    toast("📥 Antigravity Sync", 
                          f"Nuevos agentes descargados a las {hora_actual}.", 
                          duration='short',
                          icon='https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png')
                except Exception as e:
                    print(f"⚠️ Error al mostrar la notificación: {e}")
                
    except Exception as e:
        print(f"🟥 Error en la sincronización: {e}")

# --- 5. MONITOR DE CAMBIOS (WATCHER) ---
class SincronizadorLocal(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory and ".git" not in event.src_path:
            sync_now(direction="UP")
            
    def on_created(self, event):
        if not event.is_directory and ".git" not in event.src_path:
            sync_now(direction="UP")

if __name__ == "__main__":
    event_handler = SincronizadorLocal()
    observer = Observer()
    observer.schedule(event_handler, LOCAL_REPO_PATH, recursive=True)
    observer.start()

    print("==============================================")
    print(" 🚀 SISTEMA DE AGENTES ANTIGRAVITY (PYTHON) ACTIVO ")
    print(f" 📂 Repositorio: {LOCAL_REPO_PATH}")
    print("==============================================")

    # --- 6. BUCLE DE DESCARGA (CADA 60 SEGUNDOS) ---
    try:
        while True:
            sync_now(direction="DOWN")
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo el sistema...")
        observer.stop()
    observer.join()