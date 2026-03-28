🚀 Antigravity Sync System (Windows Edition)
Este proyecto implementa un flujo de trabajo de sincronización bidireccional automática para el entorno de agentes Antigravity. Resuelve el problema de la persistencia de datos y la colaboración distribuida, permitiendo que tus agentes, configuraciones y planes de trabajo te sigan a cualquier computadora a través de GitHub.

🧠 Lo que resolvemos con este flujo
Persistencia en la Nube: Antigravity guarda localmente; nosotros lo hacemos global.

Cerebro Modular: Separamos la lógica de los agentes (Pública/Compartida) de la memoria de los proyectos (Privada).

Automatización Total: No más git push manual. El sistema "vigila" tus cambios y los sube al instante.

🛠️ Herramientas Necesarias
Para que este flujo funcione en Windows, necesitas instalar lo siguiente:

Git for Windows: El motor de versiones.

Importante: Durante la instalación, asegúrate de activar el "Git Credential Manager" para que no te pida contraseña cada vez.

PowerShell 7+: (Opcional pero recomendado) Para ejecutar los scripts de automatización con mayor estabilidad.

Cuenta de GitHub: Para alojar tus repositorios.

Antigravity SDK: El entorno de agentes de Google.

⚙️ Configuración del Sistema (Paso a Paso)
1. Preparación de la Carpeta Maestra
Elegimos una ruta de desarrollo limpia fuera de las carpetas protegidas de Windows:

Ruta: C:\src\antigravity-agents-public

2. El "Puente" (Symlink)
Usamos un Enlace Simbólico para engañar a Antigravity. La aplicación busca sus agentes en su ruta por defecto, pero Windows la redirige silenciosamente a nuestra carpeta de GitHub:

PowerShell
# Ejecutado como Administrador
mklink /D "C:\Users\TU_USUARIO\.gemini\antigravity\.agents" "C:\src\antigravity-agents-public"
3. Automatización con PowerShell (The Watcher)
El script Sync-Antigravity-Agents.ps1 realiza dos tareas críticas:

Push Instantáneo: Usa un FileSystemWatcher para detectar cuando guardas un archivo .md o una skill y lo sube a GitHub en segundos.

Pull Programado: Cada 60 segundos (o el tiempo que configures), revisa si hay actualizaciones en la nube para descargar.

4. Persistencia con Tareas Programadas
Para que el usuario no tenga que abrir consolas, configuramos una Tarea Programada de Windows:

Trigger: Al iniciar sesión (At LogOn).

Action: Ejecutar PowerShell en modo oculto (-WindowStyle Hidden).

Privilegios: Ejecutar con los privilegios más altos (necesario para el Symlink).

📂 Estructura del Ecosistema
antigravity-agents-public (Repo Público): Contiene tus Workflows y Skills. Es tu "librería de talentos" disponible para el mundo.

[App-Name]_conversation (Repo Privado): (Próximo paso) Donde vive el historial binario .pb y los documentos brain/ de cada proyecto específico.
