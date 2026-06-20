# Star-Descryptor v1.9

```
 ███████╗████████╗ █████╗ ██████╗ 
 ██╔════╝╚══██╔══╝██╔══██╗██╔══██╗
 ███████╗   ██║   ███████║██████╔╝
 ╚════██║   ██║   ██╔══██║██╔══██╗
 ███████║   ██║   ██║  ██║██║  ██║
 ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝

 ██████╗ ███████╗███████╗ ██████╗██████╗ ██╗   ██╗████████╗ ██████╗ ██████╗ 
 ██╔══██╗██╔════╝██╔════╝██╔════╝██╔══██╗╚██╗ ██╔╝╚══██╔══╝██╔═══██╗██╔══██╗
 ██║  ██║█████╗  ███████╗██║     ██████╔╝ ╚████╔╝    ██║   ██║   ██║██████╔╝
 ██║  ██║██╔══╝  ╚════██║██║     ██╔══██╗  ╚██╔╝     ██║   ██║   ██║██╔══██╗
 ██████╔╝███████╗███████║╚██████╗██║  ██║   ██║      ██║   ╚██████╔╝██║  ██║
 ╚═════╝ ╚══════╝╚══════╝ ╚═════╝╚═╝  ╚═╝   ╚═╝      ╚═╝    ╚═════╝ ╚═╝  ╚═╝
```

**by Mr-R360 | [github.com/Mr-R360](https://github.com/Mr-R360)**

---

## ⬇️ Descargas

| Plataforma | Descarga | Notas |
|---|---|---|
| 🪟 Windows | [Instalador.Star-Descrytor.exe](https://github.com/Mr-R360/Star-Descryptor/releases/tag/1.9) | Incluye todas las dependencias |
| 🐧 Linux | `git clone` (ver abajo) | Requiere Python 3 y pyodbc |

---

## ¿Qué hace?

Herramienta de línea de comandos para sistemas Wenco. Se conecta a un SQL Server, detecta automáticamente las tablas de usuarios (`USUARIO`, `USUARIOS`, `ADMINISTRADOR`) en la base de datos `BDWENCO` y muestra las contraseñas descifradas resaltadas en color. Al finalizar permite consultar otro servidor o salir.

---

## 🪟 Instalación Windows

1. Descarga el instalador desde la sección [Releases](https://github.com/Mr-R360/Star-Descryptor/releases/tag/1.9)
2. Ejecuta `Instalador.Star-Descrytor.exe` como administrador
3. Sigue el asistente de instalación
4. Abre Star-Descryptor desde el escritorio o menú inicio

> No requiere Python ni ningún software adicional.

---

## 🐧 Instalación Linux

### 1. Git
```bash
apt-get install -y git
```

### 2. Driver ODBC de Microsoft
```bash
# Descargar la clave de seguridad de Microsoft
curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | sudo gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg

# Registrar el repositorio oficial (Debian 12 / Kali)
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" | sudo tee /etc/apt/sources.list.d/mssql-release.list

# Actualizar el sistema e instalar el driver junto a las dependencias de desarrollo
sudo apt-get update && sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18 unixodbc-dev
```

### 3. Dependencias Python
```bash
# Debian / Ubuntu / Kali
apt-get install -y python3-pyodbc python3-colorama

# Kali Linux (alternativo)
pip3 install pyodbc colorama --break-system-packages
```

### 4. Clonar y ejecutar
```bash
git clone https://github.com/Mr-R360/Star-Descryptor.git
cd Star-Descryptor
python3 star_descryptor.py
```

### Actualización
```bash
cd Star-Descryptor && git pull
```

---

## Flujo de uso

Al ejecutar, el script solicita todos los parámetros antes de conectar:

```
1. IP del servidor SQL Server

2. Instancia:
   [1] Sin instancia (por defecto)
   [2] SQLEXPRESS
   [3] Ingresar manualmente

3. Credenciales:
   [1] Credenciales por defecto del sistema
   [2] sa / (ingresar contraseña)
   [3] Ingresar usuario y contraseña manualmente
```

Al terminar, el programa no se cierra — pregunta si deseas consultar otro servidor o salir.

---

## Tablas detectadas automáticamente

| Tabla | Columnas mostradas |
|---|---|
| `USUARIO` | USU_CODIGO, EMP_CODIGO, USU_NOMBRE, PWD cifrado, **PWD descifrado** |
| `USUARIOS` | USU_CODIGO, USU_NOMBRE, PWD cifrado, USU_CARGO, USU_ESTADO, USU_TIPO, **PWD descifrado** |
| `ADMINISTRADOR` | ADM_CODIGO, ADM_NOMBRE, PWD cifrado, **PWD descifrado** |

---

## Vista de resultados

- 🟡 Contraseña cifrada → en amarillo
- 🟢 **Contraseña descifrada → en verde y negrita**

---

> Herramienta de uso interno — Remoto360 Soluciones Tecnológicas
