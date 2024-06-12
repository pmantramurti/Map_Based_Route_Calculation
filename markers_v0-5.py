# HOW TO RUN
# Ensure environment has required packages installed
# run python markers_v0.5.py
# place markers on map, then hit export, then hit Get Marker Data
# Select Yes, marker reorder not functional yet
# enter pertinent details for each point, hit confirm 
# After last point, window will generate route from first to last points
#
# TODO - Option to reorder points, option to loop to first point/revisit points, generate and save trajectory and timestamps 
# at end of program

import copy
import time

from PyQt5 import sip
import folium
import os
import sys
import json
from PyQt5.QtCore import Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QSplitter, QWidget, QMainWindow, QPushButton, QGridLayout, \
    QMessageBox, QLabel, QLineEdit, QComboBox
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


class trajectory:
    def __init__(self, lat, long, height, act, first):
        self.lat = lat
        self.long = long
        self.height = height
        # 0, 1, 2 -> up, down, horizontal
        self.act = act
        # if from 1 marker to another, up then forward, up is first=true, forward is first=false
        # if just one action between markers, first=true
        self.first = first


class Map_Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.line_sequence = None
        self.map_temp = None
        self.marker_order = None
        self.points = None
        self.markers = []
        self.setWindowTitle("Route Calculator")
        self.setGeometry(100, 100, 1200, 600)
        self.setFixedSize(1400, 600)

        self.splitter = QSplitter(Qt.Horizontal, self)
        self.setCentralWidget(self.splitter)
        self.base_map = folium.Map(location=[37, -96], max_bounds=True, zoom_start=4, min_zoom=4, min_lat=22,
                                   max_lat=52, min_lon=-130, max_lon=-64)
        self.draw_map = folium.Map(location=[37, -96], max_bounds=True, zoom_start=4, min_zoom=4, min_lat=22,
                                   max_lat=52, min_lon=-130, max_lon=-64)
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
        self.draw_map.add_child(draw)
        self.web_view = QWebEngineView()
        self.web_view.setHtml(self.draw_map._repr_html_())

        self.web_view.page().profile().downloadRequested.connect(
            handle_downloadRequested
        )

        self.web_view.setMinimumSize(1000, 600)
        self.web_view.setMaximumSize(1000, 600)
        self.splitter.addWidget(self.web_view)

        self.right_panel = QWidget()
        layout = QGridLayout()
        # self.right_panel.setStyleSheet("background-color: lightblue;")
        self.right_panel.setMinimumSize(400, 600)
        self.right_panel.setMaximumSize(400, 600)
        button = QPushButton("Get Marker Data")
        button.clicked.connect(self.get_marker_data)
        layout.addWidget(button, 0, 0)
        self.right_panel.setLayout(layout)
        self.splitter.addWidget(self.right_panel)

        self.splitter.setSizes([800, 400])

    def get_marker_data(self):
        self.web_view.page().runJavaScript('''
                    var exportButton = document.getElementById('export');
                    if (exportButton) {
                        exportButton.click();
                    }''')
        wait_time = 0.1  # seconds
        max_retries = 10
        retries = 0

        while not os.path.exists('markers.json') and retries < max_retries:
            time.sleep(wait_time)
            retries += 1

        if retries == max_retries:
            raise FileNotFoundError("File 'markers.json' not found after waiting.")

        with open('markers.json', 'r') as f:
            data = json.load(f)
        if len(data['features']) > 0:
            coordinates = [feature['geometry']['coordinates'] for feature in data['features']]
            longitudes, latitudes = zip(*coordinates)
            self.points = [list(latitudes), list(longitudes)]
            self.web_view.setHtml(self.base_map._repr_html_())
            # os.remove('markers.json')
            self.get_marker_order()
        else:
            showErrorPopup('No points selected', 'Please add points first, then press export again.')

    def get_marker_order(self):
        counter = 0
        self.marker_order = list(range(len(self.points[0])))
        self.map_temp = copy.deepcopy(self.base_map)
        for lat, long in zip(self.points[0], self.points[1]):
            popup_str = lat, long
            temp_marker = folium.Marker(
                location=[lat, long],
                popup=str(popup_str),
                tooltip=str(counter),
                icon=folium.Icon(icon='info-sign')
            )
            counter += 1
            self.markers.append(temp_marker)
            self.map_temp.add_child(self.markers[-1])
        self.web_view.setHtml(self.map_temp._repr_html_())
        order_layout = QGridLayout()
        confirm_label = QLabel()
        confirm_label.setText("Are you satisfied with this order of points?\n"
                              "(mouse over the points to see their order)")
        yes_button = QPushButton()
        no_button = QPushButton()
        yes_button.setText('Yes')
        no_button.setText('No')
        order_layout.addWidget(confirm_label)
        order_layout.addWidget(yes_button)
        order_layout.addWidget(no_button)
        self.newRightPanel()
        # print('Old Layout ->', self.right_panel.layout())
        self.right_panel.setLayout(order_layout)
        yes_button.clicked.connect(self.iterate_points)

    def iterate_points(self):
        self.newSpecifyPanel(0)

    def newSpecifyPanel(self, i):
        lat, long = self.points[0][self.marker_order[i]], self.points[1][self.marker_order[i]]
        iter_layout = QGridLayout()
        top_label = QLabel()
        top_label.setText("Please enter your settings here.")
        lat_label = QLabel()
        lat_label.setText('Latitude')
        lat_text = QLineEdit()
        lat_text.setText(str(lat))
        long_label = QLabel()
        long_label.setText('Longitude')
        long_text = QLineEdit()
        long_text.setText(str(long))
        time_label = QLabel()
        time_label.setText('Time to next Marker (min)')
        time_text = QLineEdit()
        alt_label = QLabel()
        alt_label.setText('Altitude (m)')
        alt_text = QLineEdit()
        action_label = QLabel()
        action_label.setText('Action')
        action_options = QComboBox()
        action_options.addItems(['Takeoff', 'Landing', 'Flyover'])
        confirm_button = QPushButton()
        confirm_button.setText('Confirm These Settings?')
        iter_layout.addWidget(top_label, 0, 0)
        iter_layout.addWidget(lat_label, 1, 0)
        iter_layout.addWidget(lat_text, 1, 1)
        iter_layout.addWidget(long_label, 2, 0)
        iter_layout.addWidget(long_text, 2, 1)
        iter_layout.addWidget(time_label, 3, 0)
        iter_layout.addWidget(time_text, 3, 1)
        iter_layout.addWidget(action_label, 4, 0)
        iter_layout.addWidget(action_options, 4, 1)
        iter_layout.addWidget(alt_label, 5, 0)
        iter_layout.addWidget(alt_text, 5, 1)
        iter_layout.addWidget(confirm_button, 6, 0)
        self.newRightPanel()
        confirm_button.clicked.connect(lambda: self.save_marker_input(i))
        # print('Old Layout ->', self.right_panel.layout())
        self.right_panel.setLayout(iter_layout)
        self.map_temp = copy.deepcopy(self.base_map)
        curr_mark = self.marker_order[i]
        for mark in self.marker_order:
            if mark == curr_mark:
                temp_marker = folium.Marker(
                    location=self.markers[curr_mark].location,
                    tooltip='Current Marker',
                    icon=folium.Icon(icon='info-sign', color='red')
                )
            else:
                temp_marker = folium.Marker(
                    location=self.markers[mark].location,
                    tooltip=mark,
                    icon=folium.Icon(icon='info-sign')
                )
            self.map_temp.add_child(temp_marker)
        self.web_view.setHtml(self.map_temp._repr_html_())

    def save_marker_input(self, i):
        curr_mark = self.marker_order[i]
        new_lat = self.right_panel.layout().itemAt(2).widget().text()
        new_long = self.right_panel.layout().itemAt(4).widget().text()
        flight_time = str(self.right_panel.layout().itemAt(6).widget().text() + 'min')
        action = self.right_panel.layout().itemAt(8).widget().currentText()
        new_location = [new_lat, new_long]
        new_marker = folium.Marker(
            location=new_location,
            tooltip=action,
            popup=flight_time,
            icon=folium.Icon(icon='info-sign')
        )
        self.markers[curr_mark] = new_marker
        if i + 1 < len(self.markers):
            self.newSpecifyPanel(i + 1)
        else:
            self.draw_lines()

    def draw_lines(self):
        self.newRightPanel()
        self.map_temp = copy.deepcopy(self.base_map)
        self.line_sequence = []
        for mark in self.marker_order:
            if mark != self.marker_order[-1]:
                next_mark = self.marker_order.index(mark) + 1
                self.line_sequence.append([self.markers[mark].location, self.markers[next_mark].location])
            temp_marker = folium.Marker(
                location=self.markers[mark].location,
                popup=self.markers[mark].options.get('popup'),
                tooltip=self.markers[mark].options.get('tooltip'),
                icon=folium.Icon(icon='info-sign')
            )
            self.map_temp.add_child(temp_marker)
        poly_line = folium.PolyLine(
            locations=self.line_sequence,
            color='orange',
            weight=2,
            opacity=1,
            smooth_factor=0
        )
        self.map_temp.add_child(poly_line)
        self.web_view.setHtml(self.map_temp._repr_html_())

    def newRightPanel(self):
        self.right_panel.deleteLater()
        self.right_panel = None
        self.right_panel = QWidget()
        # self.right_panel.setStyleSheet("background-color: lightblue;")
        self.right_panel.setMinimumSize(400, 600)
        self.right_panel.setMaximumSize(400, 600)
        self.splitter.addWidget(self.right_panel)


app = QApplication(sys.argv)
main_window = Map_Window()
main_window.show()
sys.exit(app.exec_())
