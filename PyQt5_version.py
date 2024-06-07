import sys
import os
import folium
from PyQt5.QtWidgets import QApplication, QSplitter, QWidget, QMainWindow
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtWebEngineWidgets import QWebEngineView


class Map_Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Route Calculator")
        self.setGeometry(100, 100, 1200, 600)

        #splitter = QSplitter(Qt.Horizontal, self)
        #self.setCentralWidget(splitter)

        self.web_view = QWebEngineView()
        self.setCentralWidget(self.web_view)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        html_file_path = os.path.join(current_dir, 'map.html')

        if not os.path.exists(html_file_path):
            print(f"Error: File {html_file_path} not found.")
            return

        self.web_view.setUrl(QUrl.fromLocalFile(html_file_path))
        QTimer.singleShot(2000, self.check_loading_status)

        placeholder_widget = QWidget()
        placeholder_widget.setStyleSheet("background-color: lightblue;")
        #splitter.addWidget(self.web_view)
        #splitter.addWidget(placeholder_widget)
        #splitter.setSizes([800, 400])

    def check_loading_status(self):
        print("Loading Map...")
        self.web_view.page().runJavaScript("console.log('JavaScript is working');")


m = folium.Map(location=[37, -96], max_bounds=True, zoom_start=4, min_zoom=4, min_lat=22, max_lat=52,
               min_lon=-130, max_lon=-64)
m.save("map.html")

app = QApplication(sys.argv)
main_window = Map_Window()
main_window.show()
sys.exit(app.exec_())
