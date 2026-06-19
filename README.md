# Star-Descryptor v1.8

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

**by Mr-R360 | [remoto360.com](https://remoto360.com)**

---

## ¿Qué hace?

Herramienta de línea de comandos para sistemas Wenco. Se conecta a un SQL Server, detecta automáticamente las tablas de usuarios (`USUARIO`, `USUARIOS`, `ADMINISTRADOR`) en la base de datos `BDWENCO` y muestra las contraseñas descifradas resaltadas en color.

---

## Requisitos

### 1. Git
```bash
apt-get install -y git
```

### 2. Driver ODBC de Microsoft
```bash
curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /usr/share/keyrings/microsoft-prod.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list
apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18 unixodbc-dev
```

### 3. Dependencias Python
```bash
# Debian / Ubuntu
apt-get install -y python3-pyodbc python3-colorama

# Kali Linux
pip3 install pyodbc colorama --break-system-packages
```

---

## Instalación

```bash
git clone https://github.com/Mr-R360/Star-Descryptor.git
cd Star-Descryptor
python3 star_descryptor.py
```

## Actualización

```bash
cd Star-Descryptor
git pull
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

Una vez ingresados los datos, conecta directamente sin reintentos lentos.

---

## Tablas detectadas automáticamente

| Tabla | Columnas mostradas |
|---|---|
| `USUARIO` | USU_CODIGO, EMP_CODIGO, USU_NOMBRE, PWD cifrado, PWD descifrado |
| `USUARIOS` | USU_CODIGO, USU_NOMBRE, PWD cifrado, USU_CARGO, USU_ESTADO, USU_TIPO, PWD descifrado |
| `ADMINISTRADOR` | ADM_CODIGO, ADM_NOMBRE, PWD cifrado, EMAIL, CARGO, PWD descifrado |

Si una tabla no existe o está vacía, se indica y continúa con las demás.

---

## Vista de resultados

- 🟡 **Contraseña cifrada** → resaltada en amarillo  
- 🟢 **Contraseña descifrada** → resaltada en verde y negrita

---

> Herramienta de uso interno — Remoto360 Soluciones Tecnológicas
