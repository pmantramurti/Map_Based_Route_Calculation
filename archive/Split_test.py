import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QSplitter, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView

class Test_Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Two-Section Window")
        self.setGeometry(100, 100, 1200, 600)
        self.setFixedSize(1200, 600)

        splitter = QSplitter(Qt.Horizontal, self)
        self.setCentralWidget(splitter)
        section1_widget = QWebEngineView()
        section1_widget.setMinimumSize(800, 600)
        section1_widget.setMaximumSize(800, 600)
        splitter.addWidget(section1_widget)

        section2_widget = QWidget()
        section2_widget.setStyleSheet("background-color: lightblue;")
        section2_widget.setMinimumSize(400, 600)
        section2_widget.setMaximumSize(400, 600)
        splitter.addWidget(section2_widget)
        splitter.setSizes([800, 400])

def main():
    app = QApplication(sys.argv)
    main_window = Test_Window()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
