import folium
import tkinter as tk
from tkinterweb import HtmlFrame
import os

# folium.Marker(
#    location=[40.7128, -74.0060],  # New York City coordinates
#    popup='Start Point',
#    icon=folium.Icon(icon='info-sign')
# ).add_to(m)

m = folium.Map(location=[37, -96], max_bounds=True, zoom_start=4, min_zoom=4, min_lat=24, max_lat=50,
               min_lon=-125, max_lon=-67)
m.save("map.html")
window = tk.Tk()
window.title("Route Selection")
window.geometry("800x600")
map_frame = HtmlFrame(window, horizontal_scrollbar="auto", vertical_scrollbar="auto")
map_frame.pack(fill="both", expand=True)

full_path = os.path.abspath("map.html")
repStr = "\\"
file_url = f'file:///{full_path.replace(repStr, "/")}'

map_frame.load_file(file_url)
#sample_html = """<!DOCTYPE html>
#<html>
#<body>
#<h1>Hello, World!</h1>
#<p>This is a test.</p>
#</body>
#</html>"""
#map_frame.load_html(sample_html)
window.mainloop()
