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
BRANCH = "main"
ICON_PATH = r"C:\src\github_icon.png" 

# --- 1. PREPARACIÓN DE ENTORNO ---
if not os.path.exists(LOCAL_REPO_PATH): 
    os.makedirs(LOCAL_REPO_PATH, exist_ok=True)

if not os.path.exists(ICON_PATH):
    try:
        # Descarga de icono oficial para que la notificación se vea profesional
        urllib.request.urlretrieve("https://cdn-icons-png.flaticon.com/512/25/25231.png", ICON_PATH)
    except:
        pass

# --- 2. VÍNCULO CON ANTIGRAVITY (SYMLINK) ---
if not os.path.exists(ANTIGRAVITY_PATH):
    print("🟨 Creando enlace simbólico para Antigravity...")
    try:
        subprocess.run(["cmd", "/c", "mklink", "/D", ANTIGRAVITY_PATH, LOCAL_REPO_PATH], check=True)
    except subprocess.CalledProcessError:
        print("❌ Error: Ejecuta como Administrador para crear el Symlink.")

# --- 3. FUNCIÓN DE NOTIFICACIÓN (REFORZADA) ---
def avisar(titulo, mensaje, link):
    print(f"📣 Notificando: {titulo}...")
    try:
        toast(
            titulo, 
            mensaje, 
            duration='short', 
            icon=ICON_PATH if os.path.exists(ICON_PATH) else None, 
            on_click=link,
            app_id='AntigravitySync' # Identificador para que Windows no la bloquee
        )
    except Exception as e:
        print(f"⚠️ Error visual de Windows: {e}")

# --- 4. FUNCIÓN DE SINCRONIZACIÓN ---
def sync_now(direction):
    hora = datetime.now().strftime('%H:%M:%S')
    os.chdir(LOCAL_REPO_PATH)

    try:
        if direction == "UP":
            # Pequeña pausa para que el editor de texto suelte el archivo
            time.sleep(0.7) 
            
            subprocess.run(["git", "add", "."], capture_output=True)
            status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
            
            if status.stdout.strip():
                archivos = len(status.stdout.strip().split('\n'))
                print(f"🚀 [DETECTADO] {archivos} cambios locales. Subiendo...")
                
                subprocess.run(["git", "commit", "-m", f"Auto-sync {hora}"], capture_output=True)
                res = subprocess.run(["git", "push", "origin", BRANCH], capture_output=True, text=True)
                
                if res.returncode == 0:
                    print(f"🟩 >>> [{hora}] SUBIDA EXITOSA")
                    avisar("🚀 Respaldo en GitHub", f"Se han subido {archivos} archivo(s) correctamente.", LOCAL_REPO_PATH)
                else:
                    print(f"🟥 Error en Push: {res.stderr}")
        
        elif direction == "DOWN":
            res = subprocess.run(["git", "pull", "origin", BRANCH, "--rebase"], capture_output=True, text=True)
            salida = res.stdout.lower() + res.stderr.lower()
            
            if "already up to date" not in salida and "actualizado" not in salida:
                print(f"⬜ --- [{hora}] DESCARGA DETECTADA")
                avisar("📥 Nuevos Agentes", "Se han descargado cambios desde la nube.", LOCAL_REPO_PATH)
                
    except Exception as e:
        print(f"💥 Error crítico: {e}")

# --- 5. MONITOR DE ARCHIVOS (WATCHDOG) ---
class SincronizadorLocal(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory and ".git" not in event.src_path:
            sync_now("UP")
    def on_created(self, event):
        if not event.is_directory and ".git" not in event.src_path:
            sync_now("UP")

# --- 6. EJECUCIÓN PRINCIPAL ---
if __name__ == "__main__":
    # Prueba inicial para verificar que las notificaciones funcionan al arrancar
    avisar("🔥 Antigravity Online", "El motor de sincronización está en marcha.", LOCAL_REPO_PATH)
    
    event_handler = SincronizadorLocal()
    observer = Observer()
    observer.schedule(event_handler, LOCAL_REPO_PATH, recursive=True)
    observer.start()

    print("==============================================")
    print(" ✅ SISTEMA DE AGENTES SINCRONIZADO ")
    print(f" 📂 Ruta: {LOCAL_REPO_PATH}")
    print("==============================================")

    try:
        while True:
            sync_now("DOWN")
            time.sleep(60) # Revisa GitHub cada minuto
    except KeyboardInterrupt:
        print("🛑 Deteniendo...")
        observer.stop()
    observer.join()