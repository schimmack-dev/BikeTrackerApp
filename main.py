import sys
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy_garden.mapview import MapView, MapMarkerPopup
from kivy.graphics import Color, Line

try:
    from plyer import gps
except ImportError:
    gps = None

class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gps_started = False
        self.distance = 0.0
        self.last_lat = None
        self.last_lon = None
        self.mock_event = None
        self.track_points = []
        self.track_line = None
        self.start_marker = None
        self.end_marker = None

    def start_gps(self):
        self.reset_tracking()  # Track zurücksetzen beim Start
        if sys.platform == "darwin":
            self.ids.status_label.text = "macOS erkannt – Mock GPS aktiviert"
            if not self.mock_event:
                self.mock_event = Clock.schedule_interval(self.mock_gps_update, 5)
                print("Mock GPS gestartet")
        else:
            if gps:
                try:
                    gps.configure(on_location=self.on_location)
                    gps.start()
                    self.gps_started = True
                    self.ids.status_label.text = "GPS gestartet"
                except NotImplementedError:
                    self.ids.status_label.text = "GPS nicht verfügbar"
                except Exception as e:
                    self.ids.status_label.text = f"Fehler beim Starten von GPS: {e}"
            else:
                self.ids.status_label.text = "Plyer GPS-Modul nicht gefunden"

    def stop_gps(self):
        if sys.platform == "darwin":
            if self.mock_event:
                self.mock_event.cancel()
                self.mock_event = None
                self.ids.status_label.text = "Mock GPS gestoppt"
                print("Mock GPS gestoppt")
        else:
            if self.gps_started and gps:
                try:
                    gps.stop()
                    self.gps_started = False
                    self.ids.status_label.text = "GPS gestoppt"
                    print("GPS gestoppt")
                except Exception as e:
                    self.ids.status_label.text = f"Fehler beim Stoppen von GPS: {e}"

    def reset_tracking(self):
        self.distance = 0.0
        self.last_lat = None
        self.last_lon = None
        self.track_points = []
        self.ids.distance_label.text = "Distanz: 0.0 km"
        self.ids.coords_label.text = "Latitude: - , Longitude: -"
        self.ids.status_label.text = "Tracking zurückgesetzt"

        mapview = self.ids.mapview
        mapview.center_on(52.5200, 13.4050)
        mapview.zoom = 12

        # Marker entfernen
        if self.start_marker:
            mapview.remove_widget(self.start_marker)
            self.start_marker = None
        if self.end_marker:
            mapview.remove_widget(self.end_marker)
            self.end_marker = None

        # Linie entfernen
        if self.track_line:
            mapview.canvas.remove(self.track_line)
            self.track_line = None

        print("Tracking und Marker zurückgesetzt")

    def on_location(self, **kwargs):
        lat = float(kwargs.get("lat", 0))
        lon = float(kwargs.get("lon", 0))
        self.ids.coords_label.text = f"Latitude: {lat:.5f}, Longitude: {lon:.5f}"

        if self.last_lat is not None and self.last_lon is not None:
            dist = ((lat - self.last_lat) ** 2 + (lon - self.last_lon) ** 2) ** 0.5 * 111
            self.distance += dist
            self.ids.distance_label.text = f"Distanz: {self.distance:.2f} km"

        self.last_lat = lat
        self.last_lon = lon

        mapview = self.ids.mapview

        # Track-Punkte speichern
        self.track_points.append((lat, lon))

        # Startmarker setzen (nur beim ersten Punkt)
        if not self.start_marker:
            self.start_marker = MapMarkerPopup(lat=lat, lon=lon)
            mapview.add_widget(self.start_marker)

        # Endmarker setzen oder verschieben
        if not self.end_marker:
            self.end_marker = MapMarkerPopup(lat=lat, lon=lon)
            mapview.add_widget(self.end_marker)
        else:
            self.end_marker.lat = lat
            self.end_marker.lon = lon

        mapview.center_on(lat, lon)

        self.draw_track_line()

    def draw_track_line(self):
        if len(self.track_points) < 2:
            return

        mapview = self.ids.mapview
        points = []
        for lat, lon in self.track_points:
            x, y = mapview.get_window_xy_from(lat, lon, mapview.zoom)
            points.extend([x, y])

        # Alte Linie entfernen
        if self.track_line:
            mapview.canvas.remove(self.track_line)

        with mapview.canvas:
            Color(1, 0, 0, 1)
            self.track_line = Line(points=points, width=2)

    def mock_gps_update(self, dt):
        import random
        lat = 52.5200 + random.uniform(-0.001, 0.001)
        lon = 13.4050 + random.uniform(-0.001, 0.001)
        self.on_location(lat=lat, lon=lon)


class BikeApp(App):
    def build(self):
        return MainLayout()

if __name__ == "__main__":
    BikeApp().run()
