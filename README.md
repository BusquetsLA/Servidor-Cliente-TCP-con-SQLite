# Propuesta Formativa Obligatoria 1 - programación sobre redes
# Servidor/Cliente TCP con SQLite (Python)

Este proyecto implementa un **servidor TCP** en `localhost:5000` que recibe mensajes de clientes, los guarda en una **base de datos SQLite** y responde con una confirmación que incluye un **timestamp**. Incluye un **cliente** para pruebas.

## Estructura:
- `server.py`: servidor con modularización y comentarios.
- `client.py`: cliente interactivo para enviar mensajes.
- `messages.db`: se creará automáticamente al iniciar el servidor.

## Requisitos:
- Python 3.8+ (no requiere librerías externas; usa solo la librería estándar: `socket`, `sqlite3`).

## Instrucciones (Windows):
1. Abrr una terminal (PowerShell o cmd) en la carpeta del proyecto.
2. Iniciar el servidor:
   ```powershell
   python server.py
   ```
   - Si el puerto 5000 está ocupado, el servidor informará el error y saldrá.
3. En otra terminal, ejecutar el cliente:
   ```powershell
   python client.py
   ```
4. Escribir mensajes en el cliente. Para salir, teclear `éxito` o `exito`.

Cada mensaje enviado se guarda en `messages.db` con los campos:
- `id` (INTEGER, PK, autoincremental)
- `contenido` (TEXT)
- `fecha_envio` (TEXT, ISO 8601)
- `ip_cliente` (TEXT)

## Pruebas locales:
- Con el servidor corriendo, enviar:
  - Un mensaje corto ("hola").
  - Un mensaje con caracteres especiales/acentos.
  - Varios mensajes seguidos.
- Verificar en la DB (opcional):
  ```powershell
  python -c "import sqlite3; import sys;\ncon=sqlite3.connect('messages.db');\ncur=con.cursor();\nfor r in cur.execute('SELECT id, contenido, fecha_envio, ip_cliente FROM mensajes ORDER BY id DESC LIMIT 5'): print(r);\ncon.close()"
  ```

## Manejo de errores:
- Puerto ocupado o sin permisos: el servidor muestra un mensaje y finaliza.
- Base de datos inaccesible: se levanta una excepción y se cancela la inicialización.
- Errores por cliente: se registran en consola sin detener el servidor.

## Notas de diseño:
- El servidor utiliza hilos para manejar múltiples clientes simultáneamente.
- Se abre una conexión SQLite por inserción para simplificar y evitar problemas de compartición entre hilos.
- Código comentadito por secciones: configuración del socket, persistencia y manejo de clientes.
