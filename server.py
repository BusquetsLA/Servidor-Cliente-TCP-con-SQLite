import socket
import threading
import sqlite3
from datetime import datetime
from typing import Tuple

# ==============================
# Servidor TCP con SQLite
# ==============================
# Objetivo: Escuchar en localhost:5000, recibir mensajes de clientes,
# guardarlos en SQLite con (id, contenido, fecha_envio, ip_cliente)
# y responder con "Mensaje recibido: <timestamp>".
# El código está modularizado y con manejo de errores.

HOST = "127.0.0.1"  # localhost
PORT = 5000          # puerto de escucha
DB_PATH = "messages.db"


# ------------------------------
# Configuración e inicialización
# ------------------------------

def init_db(db_path: str) -> None:
    """
    Inicializa la base de datos SQLite y crea la tabla si no existe.
    Estructura: id (INTEGER PK AUTOINCREMENT), contenido (TEXT), fecha_envio (TEXT ISO8601), ip_cliente (TEXT)
    """
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS mensajes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contenido TEXT NOT NULL,
                fecha_envio TEXT NOT NULL,
                ip_cliente TEXT NOT NULL
            )
            """
        )
        conn.commit()
    except sqlite3.Error as e:
        # Error de acceso/permiso a la DB
        raise RuntimeError(f"Error al inicializar la base de datos: {e}")
    finally:
        try:
            conn.close()
        except Exception:
            pass


def init_socket(host: str, port: int) -> socket.socket:
    """
    Crea y configura el socket del servidor.
    - TCP/IP
    - Opción SO_REUSEADDR para reinicios rápidos.
    """
    try:
        # Configuración del socket TCP/IP
        srv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv_sock.bind((host, port))
        srv_sock.listen(5)  # backlog de conexiones pendientes
        print(f"[SERVIDOR] Escuchando en {host}:{port}")
        return srv_sock
    except OSError as e:
        # Ej: puerto ocupado o sin permisos
        raise RuntimeError(f"No se pudo iniciar el socket en {host}:{port}. Detalle: {e}")


# ------------------------------
# Persistencia
# ------------------------------

def save_message(db_path: str, contenido: str, ip_cliente: str, fecha_envio: str) -> None:
    """
    Guarda un mensaje en la base de datos.
    Se abre una conexión breve por inserción para simplicidad y robustez.
    """
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO mensajes (contenido, fecha_envio, ip_cliente) VALUES (?, ?, ?)",
            (contenido, fecha_envio, ip_cliente),
        )
        conn.commit()
    except sqlite3.Error as e:
        # Se propaga como RuntimeError para una traza homogénea en el servidor
        raise RuntimeError(f"Error al guardar mensaje en DB: {e}")
    finally:
        try:
            conn.close()
        except Exception:
            pass


# ------------------------------
# Manejo de clientes
# ------------------------------

def handle_client(conn: socket.socket, addr: Tuple[str, int], db_path: str) -> None:
    """
    Atiende a un cliente individual:
    - Recibe datos
    - Inserta en DB
    - Responde confirmación con timestamp
    - Maneja errores por cliente sin comprometer el servidor general
    """
    client_ip, client_port = addr
    try:
        with conn:
            # Recibir hasta 4096 bytes por mensaje
            data = conn.recv(4096)
            if not data:
                return
            mensaje = data.decode("utf-8", errors="replace").strip()

            # Timestamp en formato ISO 8601
            ts = datetime.now().isoformat(timespec="seconds")

            # Guardar en DB
            save_message(db_path, mensaje, client_ip, ts)

            # Responder al cliente
            respuesta = f"Mensaje recibido: {ts}"
            conn.sendall(respuesta.encode("utf-8"))

            print(f"[SERVIDOR] ({client_ip}:{client_port}) -> '{mensaje}' | guardado: {ts}")
    except Exception as e:
        # Loguea el error sin tumbar el servidor
        print(f"[ERROR] Fallo atendiendo a {client_ip}:{client_port} -> {e}")


def accept_loop(srv_sock: socket.socket, db_path: str) -> None:
    """
    Bucle principal de aceptación de conexiones entrantes.
    Lanza un hilo por cliente para no bloquear el servidor.
    """
    try:
        while True:
            conn, addr = srv_sock.accept()
            # Crear un hilo por cliente para manejo concurrente
            t = threading.Thread(target=handle_client, args=(conn, addr, db_path), daemon=True)
            t.start()
    except KeyboardInterrupt:
        print("\n[SERVIDOR] Interrupción por teclado. Cerrando...")
    finally:
        try:
            srv_sock.close()
        except Exception:
            pass


# ------------------------------
# Punto de entrada
# ------------------------------

def run_server() -> None:
    """
    Orquesta la inicialización de DB y socket, y lanza el bucle de aceptación.
    """
    # Inicializar DB
    init_db(DB_PATH)

    # Inicializar socket y entrar al accept loop
    srv_sock = init_socket(HOST, PORT)
    accept_loop(srv_sock, DB_PATH)


if __name__ == "__main__":
    run_server()
