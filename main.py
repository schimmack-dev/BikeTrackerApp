import sys
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy_garden.mapview import MapView, MapMarkerPopup

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

    def start_gps(self):
        if sys.platform == "darwin":
            # macOS: Mock GPS (da kein echtes GPS)
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
                    print("Echtes GPS gestartet")
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
        self.ids.distance_label.text = "Distanz: 0.0 km"
        self.ids.coords_label.text = "Latitude: - , Longitude: -"
        self.ids.status_label.text = "Tracking zurückgesetzt"

        mapview = self.ids.mapview
        mapview.center_on(52.5200, 13.4050)
        mapview.zoom = 12
        # Alle Marker entfernen
        for child in list(mapview.children):
            if isinstance(child, MapMarkerPopup):
                mapview.remove_widget(child)
        print("Tracking und Marker zurückgesetzt")

    def on_location(self, **kwargs):
        lat = float(kwargs.get("lat", 0))
        lon = float(kwargs.get("lon", 0))
        self.ids.coords_label.text = f"Latitude: {lat:.5f}, Longitude: {lon:.5f}"

        if self.last_lat is not None and self.last_lon is not None:
            # Sehr einfache Distanzberechnung (Pythagoras * ca. 111km pro Grad)
            dist = ((lat - self.last_lat) ** 2 + (lon - self.last_lon) ** 2) ** 0.5 * 111
            self.distance += dist
            self.ids.distance_label.text = f"Distanz: {self.distance:.2f} km"

        self.last_lat = lat
        self.last_lon = lon

        mapview = self.ids.mapview
        marker = MapMarkerPopup(lat=lat, lon=lon)
        mapview.add_widget(marker)
        mapview.center_on(lat, lon)

    def mock_gps_update(self, dt):
        import random
        lat = 52.5200 + random.uniform(-0.001, 0.001)
        lon = 13.4050 + random.uniform(-0.001, 0.001)
        self.on_location(lat=lat, lon=lon)

    def save_track(self):
        # Platzhalter: Track speichern (z.B. in Datei)
        self.ids.status_label.text = "Track gespeichert (nicht implementiert)"
        print("Track speichern: Funktion noch nicht implementiert")


class BikeApp(App):
    def build(self):
        return MainLayout()


if __name__ == "__main__":
    BikeApp().run()
