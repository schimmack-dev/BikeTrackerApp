import sys
import json
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock

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
        self.track_points = []  # Liste für GPS-Datenpunkte

        self.load_track()

    def save_track(self):
        with open("track.json", "w") as f:
            json.dump(self.track_points, f)

    def load_track(self):
        if os.path.exists("track.json"):
            with open("track.json", "r") as f:
                self.track_points = json.load(f)
            # Letzten Punkt anzeigen, falls vorhanden
            if self.track_points:
                last_point = self.track_points[-1]
                lat, lon = last_point["lat"], last_point["lon"]
                self.ids.coords_label.text = f"Latitude: {lat:.5f}, Longitude: {lon:.5f}"
                # Optional: Distance aktualisieren, falls gewünscht

    def start_gps(self):
        if sys.platform == "darwin":
            self.ids.status_label.text = "macOS erkannt – Mock GPS aktiviert"
            Clock.schedule_interval(self.mock_gps_update, 5)
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
        if self.gps_started and gps:
            try:
                gps.stop()
                self.gps_started = False
                self.ids.status_label.text = "GPS gestoppt"
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
        # Track-Datei löschen
        if os.path.exists("track.json"):
            os.remove("track.json")

    def on_location(self, **kwargs):
        lat = float(kwargs.get("lat", 0))
        lon = float(kwargs.get("lon", 0))
        self.ids.coords_label.text = f"Latitude: {lat:.5f}, Longitude: {lon:.5f}"

        if self.last_lat is not None and self.last_lon is not None:
            dist = ((lat - self.last_lat)**2 + (lon - self.last_lon)**2)**0.5 * 111  # grobe km-Berechnung
            self.distance += dist
            self.ids.distance_label.text = f"Distanz: {self.distance:.2f} km"

        self.last_lat = lat
        self.last_lon = lon

        # GPS-Punkt speichern
        self.track_points.append({"lat": lat, "lon": lon})
        self.save_track()

    def mock_gps_update(self, dt):
        import random
        lat = 52.5200 + random.uniform(-0.0005, 0.0005)
        lon = 13.4050 + random.uniform(-0.0005, 0.0005)
        self.on_location(lat=lat, lon=lon)

class BikeApp(App):
    def build(self):
        return MainLayout()

if __name__ == '__main__':
    BikeApp().run()
