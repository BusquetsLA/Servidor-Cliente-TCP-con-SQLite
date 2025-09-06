import socket
from typing import Optional

# ==============================
# Cliente TCP para pruebas
# ==============================
# Se conecta a localhost:5000 y permite enviar mensajes
# hasta que el usuario escriba 'éxito' o 'exito'.
# Muestra la respuesta del servidor para cada envío.

HOST = "127.0.0.1"
PORT = 5000


def connect_to_server(host: str, port: int) -> socket.socket:
    """
    Intenta conectarse al servidor TCP en host:port.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        return sock
    except OSError as e:
        raise RuntimeError(f"No se pudo conectar al servidor en {host}:{port}. Detalle: {e}")


def send_message(sock: socket.socket, message: str) -> Optional[str]:
    """
    Envía un mensaje y devuelve la respuesta del servidor, o None si no hay respuesta.
    """
    try:
        sock.sendall(message.encode("utf-8"))
        data = sock.recv(4096)
        if not data:
            return None
        return data.decode("utf-8", errors="replace")
    except OSError as e:
        raise RuntimeError(f"Error enviando/recibiendo datos: {e}")


def main() -> None:
    print("[CLIENTE] Ingrese mensajes para enviar al servidor.")
    print("[CLIENTE] Escriba 'éxito' o 'exito' para finalizar.\n")

    while True:
        texto = input("> ").strip()
        if texto.lower() in ("éxito", "exito"):
            print("[CLIENTE] Finalizando.")
            break

        try:
            # Crear una conexión por mensaje para simplificar el flujo
            with connect_to_server(HOST, PORT) as sock:
                respuesta = send_message(sock, texto)
                if respuesta is None:
                    print("[CLIENTE] Sin respuesta del servidor.")
                else:
                    print(f"[SERVIDOR] {respuesta}")
        except Exception as e:
            print(f"[ERROR] {e}")


if __name__ == "__main__":
    main()
