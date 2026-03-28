# 🌌 Antigravity Sync System (Windows Engine)

### *The Ultimate Bidirectional Bridge for Google's Agentic Workflows*

![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-blue?logo=windows)
![PowerShell](https://img.shields.io/badge/Script-PowerShell%207-blue?logo=powershell)
![Engine](https://img.shields.io/badge/Engine-Git-orange?logo=git)

---

## 🎯 **¿Qué es este Proyecto?**

Este sistema resuelve el "eslabón perdido" de **Antigravity**. Por defecto, tus agentes y conversaciones viven atrapados localmente. Este flujo transforma tu entorno en un **ecosistema modular en la nube**, permitiendo que tus agentes y progresos se sincronicen automáticamente entre múltiples computadoras usando **GitHub** como cerebro central.

### **¿Por qué usar este flujo?**

* **🔄 Sincronización Invisible:** No más `git push` manual. Si guardas un cambio, ya está en la nube.
* **🧠 Arquitectura Modular:** Separamos tus **Agentes** (Lógica Pública) de tus **Conversaciones** (Memoria Privada).
* **💻 Portabilidad Total:** Cambia de PC y retoma tu conversación exactamente donde la dejaste.

---

## 🛠️ **Herramientas Necesarias**

Instala estas herramientas para asegurar la compatibilidad total:

| Herramienta | Función | Link de Descarga |
| :--- | :--- | :--- |
| 🧩 **Git for Windows** | Motor de control de versiones. | [📥 Descargar](https://gitforwindows.org/) |
| ⚡ **PowerShell 7+** | Ejecución de scripts estable. | [📥 Descargar](https://github.com/PowerShell/PowerShell/releases) |
| 📝 **VS Code** | Editor recomendado. | [📥 Descargar](https://code.visualstudio.com/) |

---

## 🚀 **Guía de Instalación Rápida**

### **1️⃣ Preparar el Terreno**

Crea la carpeta maestra donde vivirán tus agentes:

```powershell
mkdir C:\src\antigravity-agents-public
```

### **2️⃣ El Puente de Datos (Symlink)**

⚠️ IMPORTANTE: Ejecuta PowerShell como Administrador.

Engañamos a Antigravity para que redirija su lectura a nuestra carpeta de GitHub.

```powershell
# Reemplaza 'TU_USUARIO' con tu nombre real de Windows
$user = $env:USERNAME
mklink /D "C:\Users\$user\.gemini\antigravity\.agents" "C:\src\antigravity-agents-public"
```

### **3️⃣ Activar el Motor de Sincronización**

El script Sync-Antigravity-Agents.ps1 vigila tus archivos. Configúralo en el Programador de Tareas:

**Disparador:** Al iniciar sesión (At LogOn).

**Acción:** powershell.exe

**Argumentos:**

```powershell
-WindowStyle Hidden -ExecutionPolicy Bypass -File "C:\src\scripts\Sync-Antigravity-Agents.ps1"
```

---

## 📂 **Estructura del Ecosistema**

```
C:\src\
├── 🤖 antigravity-agents-public/  # [REPO PÚBLICO] Workflows & Skills
├── 📂 scripts/                    # Scripts de automatización (.ps1)
└── 🔐 [App-Name]_conversation/    # [REPO PRIVADO] Historial de chats (.pb)
```

---

## 🤝 **Contribuciones**

¡Este es un proyecto abierto! Si tienes una idea para mejorar el script de PowerShell, abre un Pull Request.
