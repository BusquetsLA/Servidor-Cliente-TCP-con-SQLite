import argparse
import sqlite3
import sys
from pathlib import Path

# ==============================
# Script: inspect_db
# ==============================
# Consulta y muestra los últimos N registros de la tabla 'mensajes'
# en la base de datos SQLite utilizada por el servidor.
#
# Uso:
#   python inspect_db.py --db messages.db --limit 10
#
# Parámetros:
#   --db/-d     Ruta a la base de datos (por defecto: messages.db)
#   --limit/-n  Cantidad de filas a mostrar (por defecto: 10)
#
# Notas:
# - No requiere dependencias externas.
# - Maneja errores comunes (archivo inexistente, tabla ausente).


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspecciona los últimos registros de messages.db")
    parser.add_argument("--db", "-d", default="messages.db", help="Ruta al archivo SQLite (default: messages.db)")
    parser.add_argument("--limit", "-n", type=int, default=10, help="Cantidad de filas a mostrar (default: 10)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    db_path = Path(args.db)

    if not db_path.exists():
        print(f"[ERROR] No se encontró la base de datos en: {db_path}")
        return 1

    try:
        con = sqlite3.connect(str(db_path))
        cur = con.cursor()
        # Verificar que la tabla exista
        cur.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='mensajes'
        """)
        if cur.fetchone() is None:
            print("[ERROR] La tabla 'mensajes' no existe en la base de datos.")
            return 1

        # Consultar últimos N registros
        cur.execute(
            "SELECT id, contenido, fecha_envio, ip_cliente FROM mensajes ORDER BY id DESC LIMIT ?",
            (args.limit,),
        )
        rows = cur.fetchall()

        if not rows:
            print("[INFO] No hay registros en la tabla 'mensajes'.")
            return 0

        print(f"Últimos {len(rows)} registro(s) en '{db_path}':\n")
        for r in rows:
            # r: (id, contenido, fecha_envio, ip_cliente)
            print(f"id={r[0]} | fecha={r[2]} | ip={r[3]} | contenido={r[1]}")

        return 0
    except sqlite3.Error as e:
        print(f"[ERROR] Fallo al consultar la base de datos: {e}")
        return 1
    finally:
        try:
            con.close()
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())
