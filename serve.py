"""Run the existing UI locally or behind a cloud HTTP proxy."""
import os
import threading
import webbrowser

from app import app, load_model, model_info
from waitress import create_server


def main():
    load_model()
    print('MODEL STATUS:', model_info(), flush=True)
    cloud = bool(os.environ.get('RENDER') or os.environ.get('PORT'))
    port = int(os.environ.get('PORT', '8000'))
    host = os.environ.get('HOST', '0.0.0.0' if cloud else '127.0.0.1')
    url = f'http://127.0.0.1:{port}/#support'
    server = create_server(app, host=host, port=port, threads=4)
    print(f'READY: listening on {host}:{port}', flush=True)
    if os.environ.get('MM_OPEN_BROWSER', '0' if cloud else '1') == '1':
        timer = threading.Timer(1.2, lambda: webbrowser.open(url))
        timer.daemon = True
        timer.start()
    try:
        server.run()
    finally:
        server.close()


if __name__ == '__main__':
    main()
