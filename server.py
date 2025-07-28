import http.server
import socketserver

PORT = 8000
Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Servidor iniciado en el puerto {PORT}")
    print(f"Abre tu navegador en http://localhost:{PORT}")
    httpd.serve_forever()
