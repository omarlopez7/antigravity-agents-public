🌌 **Antigravity Sync System (Windows Engine)**
The Ultimate Bidirectional Bridge for Google’s Agentic Workflows

🎯 **¿Qué es este Proyecto?**
Este sistema resuelve el "eslabón perdido" de Antigravity. Por defecto, tus agentes y conversaciones viven atrapados localmente. Este flujo transforma tu entorno en un ecosistema modular en la nube, permitiendo que tus agentes y progresos se sincronicen automáticamente entre múltiples computadoras usando GitHub como cerebro central.

**¿Por qué usar este flujo?**
🔄 Sincronización Invisible: No más git push manual. Si guardas un cambio, ya está en la nube.
🧠 Arquitectura Modular: Separamos tus Agentes (Lógica Pública) de tus Conversaciones (Memoria Privada).
💻 Portabilidad Total: Cambia de PC y retoma tu conversación exactamente donde la dejaste.

🛠️ **Herramientas Necesarias**
Instala estas herramientas para asegurar la compatibilidad total:

Herramienta                  Función                         
🧩 Git for Windows           Motor de control de versiones. 
⚡ PowerShell 7+             Ejecución de scripts estable.  
📝 VS Code                   Editor recomendado.            


🚀**Guía de Instalación Rápida**

1️⃣ Preparar el TerrenoCrea la carpeta maestra donde vivirán tus agentes:PowerShellmkdir C:\src\antigravity-agents-public

2️⃣ El Puente de Datos (Symlink)⚠️ IMPORTANTE: Ejecuta PowerShell como Administrador.
PowerShell# Reemplaza 'TU_USUARIO' con tu nombre real de Windows
$user = $env:USERNAME
mklink /D "C:\Users\$user\.gemini\antigravity\.agents" "C:\src\antigravity-agents-public"

3️⃣ Activar el Motor de SincronizaciónEl script Sync-Antigravity-Agents.ps1 vigila tus archivos. 
Configúralo en el Programador de Tareas:Disparador: Al iniciar sesión (At LogOn).
Acción: powershell.exeArgumentos: -WindowStyle Hidden -ExecutionPolicy Bypass -File "C:\src\scripts\Sync-Antigravity-Agents.ps1"

📂 **Estructura del Ecosistema**
BashC:\src\
├── 🤖 antigravity-agents-public/  # [REPO PÚBLICO] Workflows & Skills
├── 📂 scripts/                    # Scripts de automatización (.ps1)
└── 🔐 [App-Name]_conversation/    # [REPO PRIVADO] Historial de chats (.pb)

🤝 **Contribuciones**
¡Este es un proyecto abierto! Si tienes una idea para mejorar el script de PowerShell, abre un Pull Request.

Desarrollado para la comunidad de IA Generativa.
