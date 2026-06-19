# ⭐ Star-Descryptor v1.4

```
  _____ _______ _    ____      ____  _____ ___  ____ ____  _____  _____  ___  ____
 / ___|___ /   / |  |  _ \    |  _ \| ____/ __|/ ___|  _ \|_   _|/ _ \ |  _ \
 \___ \ |_ \  / /   | | | |   | | | |  _| \___ \ |   | |_) | | || | | || |_) |
  ___) |__) |/ /_   | |_| |   | |_| | |___ ___) | |___| _ <  | || |_| ||  _ <
 |____/____/|____|  |____/    |____/|_____|____/ \____|_| \_\ |_| \___/ |_| \_\
```

**by mr.r360 | [remoto360.com](https://remoto360.com)**

---

## ¿Qué hace?

Herramienta de línea de comandos que se conecta a un servidor SQL Server con sistema Wenco, lee la tabla `BDWENCO.dbo.USUARIO` y descifra las contraseñas usando el algoritmo Frankenstein dinámico.

## Requisitos

```bash
# Debian/Ubuntu — Driver ODBC
curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /usr/share/keyrings/microsoft-prod.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list
apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18 unixodbc-dev

# pyodbc
apt-get install python3-pyodbc

# Kali Linux
pip3 install pyodbc --break-system-packages
```

## Instalación y uso

```bash
git clone https://github.com/Mr-R360/Star-Descryptor.git
cd Star-Descryptor
python3 star_descryptor.py
```

## Flujo de conexión

1. Pide la IP del servidor
2. Prueba automáticamente `SOPORTE / SOPORTE`
3. Si falla → pide contraseña del usuario `sa`
4. Si sigue fallando → pide nombre de instancia y reintenta

---
> Herramienta de uso interno — Remoto360 Soluciones Tecnológicas
