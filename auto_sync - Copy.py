import os
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- CONFIGURACIÓN ---
PATH_A_VIGILAR = r"C:\src\antigravity-agents-public"
INTERVALO_PULL = 3600  # Descarga cambios de la nube cada 1 hora (segundos)

class GitWatcher(FileSystemEventHandler):
    """Esta clase es el 'Vigilante'. Reacciona cuando guardas archivos."""
    
    def on_modified(self, event):
        # Ignoramos carpetas y archivos temporales o del propio Git
        if event.is_directory or ".git" in event.src_path:
            return
        
        print(f"📝 Cambio detectado en: {event.src_path}")
        self.ejecutar_sync(event.src_path)

    def ejecutar_sync(self, file_path):
        # Buscamos la carpeta raíz del repositorio (donde está el .git)
        repo_dir = self.buscar_raiz_git(os.path.dirname(file_path))
        
        if repo_dir:
            try:
                print(f"📦 Sincronizando repo: {os.path.basename(repo_dir)}...")
                # Cambiamos a la carpeta del repo
                os.chdir(repo_dir)
                
                # Comandos de Git
                subprocess.run(["git", "add", "."], check=True, capture_output=True)
                # El commit solo se hace si hay algo nuevo
                subprocess.run(["git", "commit", "-m", "Auto-sync via Python"], capture_output=True)
                subprocess.run(["git", "push"], check=True, capture_output=True)
                
                print(f"✅ ¡Subida exitosa a GitHub!")
            except subprocess.CalledProcessError as e:
                print(f"⚠️ Nota: No había cambios nuevos para subir o hubo un error de red.")
        else:
            print("❌ No se encontró un repositorio Git para este archivo.")

    def buscar_raiz_git(self, ruta):
        """Busca hacia arriba hasta encontrar la carpeta .git"""
        while ruta != os.path.dirname(ruta): # Mientras no lleguemos al disco C:
            if os.path.exists(os.path.join(ruta, ".git")):
                return ruta
            ruta = os.path.dirname(ruta)
        return None

if __name__ == "__main__":
    # 1. Iniciamos el Vigilante de cambios (Push)
    event_handler = GitWatcher()
    observer = Observer()
    observer.schedule(event_handler, PATH_A_VIGILAR, recursive=True)
    
    print(f"🚀 MOTOR DE SYNC ACTIVADO")
    print(f"👀 Vigilando: {PATH_A_VIGILAR}")
    print("Presiona Ctrl+C para detener (o cierra la ventana)")
    
    observer.start()

    # 2. Bucle para el Pull (Descarga) cada hora
    try:
        while True:
            # Aquí podrías agregar una lógica para hacer 'git pull' en todas las subcarpetas
            # Por ahora, mantenemos el script vivo
            time.sleep(10) 
    except KeyboardInterrupt:
        observer.stop()
    observer.join()