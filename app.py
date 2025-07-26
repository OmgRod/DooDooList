import sys
import threading
import time
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, QTimer, pyqtSlot
import requests
import uvicorn

def start_server():
    uvicorn.run("server:app", host="127.0.0.1", port=8000, log_level="info")

class LoaderWebView(QWebEngineView):
    def __init__(self):
        super().__init__()
        self.health_timer = QTimer()
        self.health_timer.timeout.connect(self.check_health)
        self.health_timer.start(1000)

    @pyqtSlot()
    def check_health(self):
        try:
            r = requests.get("http://127.0.0.1:8000/health", timeout=0.5)
            if r.status_code == 200:
                self.health_timer.stop()
                url = f"http://127.0.0.1:8000/?_={int(time.time())}"
                self.load(QUrl(url))
                self.show()
        except requests.exceptions.RequestException:
            pass

def main():
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    app = QApplication(sys.argv)
    app.setApplicationName("Doo-Doo List")
    app.setApplicationDisplayName("Doo-Doo List")
    web = LoaderWebView()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
