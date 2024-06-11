import folium
import os
import sys
import json
from PyQt5.QtCore import Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QSplitter, QWidget, QMainWindow, QPushButton, QGridLayout, QMessageBox
from folium.plugins import Draw

current_folder = os.path.dirname(os.path.abspath(__file__))


def handle_downloadRequested(item):
    path = os.path.join(current_folder, item.suggestedFileName())
    if path:
        item.setPath(path)
        item.accept()


def showErrorPopup(error, message):
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Critical)
    msgBox.setText(error)
    msgBox.setInformativeText(message)
    msgBox.setWindowTitle("Error")
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.exec_()


class Map_Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.points = None
        self.markers = []
        self.setWindowTitle("Route Calculator")
        self.setGeometry(100, 100, 1200, 600)
        self.setFixedSize(1400, 600)

        splitter = QSplitter(Qt.Horizontal, self)
        self.setCentralWidget(splitter)
        self.map = folium.Map(location=[37, -96], max_bounds=True, zoom_start=4, min_zoom=4, min_lat=22, max_lat=52,
                              min_lon=-130, max_lon=-64)
        draw = Draw(
            export=True,
            filename='markers.json',
            show_geometry_on_click=False,
            draw_options={
                'polyline': False,
                'rectangle': False,
                'polygon': False,
                'circle': False,
                'circlemarker': False},
            edit_options={'edit': False})
        self.map.add_child(draw)
        self.web_view = QWebEngineView()
        self.web_view.setHtml(self.map._repr_html_())

        self.web_view.page().profile().downloadRequested.connect(
            handle_downloadRequested
        )

        self.web_view.setMinimumSize(1000, 600)
        self.web_view.setMaximumSize(1000, 600)
        splitter.addWidget(self.web_view)

        self.right_panel = QWidget()
        layout = QGridLayout()
        self.right_panel.setStyleSheet("background-color: lightblue;")
        self.right_panel.setMinimumSize(400, 600)
        self.right_panel.setMaximumSize(400, 600)
        button = QPushButton("Get Marker Data")
        button.clicked.connect(self.get_marker_data)
        layout.addWidget(button, 0, 0)
        self.right_panel.setLayout(layout)
        splitter.addWidget(self.right_panel)

        splitter.setSizes([800, 400])
        self.web_view.page().runJavaScript('''
            window.onload = function() {
                var exportButton = document.getElementById('export');
                if (exportButton) {
                    exportButton.style.display = 'none';
                }
            }''')

    def get_marker_data(self):
        self.web_view.page().runJavaScript('''
                    var exportButton = document.getElementById('export');
                    if (exportButton) {
                        exportButton.style.display = 'none';
                        exportButton.click();
                    }''')
        if os.path.isfile('markers.json'):
            with open('markers.json', 'r') as f:
                data = json.load(f)
            if len(data['features']) > 0:
                coordinates = [feature['geometry']['coordinates'] for feature in data['features']]
                longitudes, latitudes = zip(*coordinates)
                self.points = [list(latitudes), list(longitudes)]
                self.web_view.setHtml(self.map._repr_html_())
                self.get_marker_order()
            else:
                showErrorPopup('No points selected', 'Please add points first, then press export again.')
        else:
            showErrorPopup('File not found', 'Please press export first.')

    def get_marker_order(self):
        for lat, long in zip(self.points[0], self.points[1]):
            print(lat, long)
            # order_layout = QGridLayout()


app = QApplication(sys.argv)
main_window = Map_Window()
main_window.show()
sys.exit(app.exec_())
