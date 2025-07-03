import sys
import json
import os
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy_garden.mapview import MapView, MapMarkerPopup
from kivy.graphics import Color, Line
from kivy.properties import ListProperty, NumericProperty, StringProperty, BooleanProperty
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.button import Button

try:
    from plyer import gps
except ImportError:
    gps = None


class MainLayout(BoxLayout):
    track_points = ListProperty([])
    distance = NumericProperty(0.0)
    speed = NumericProperty(0.0)  # km/h
    status_text = StringProperty("")

    gps_started = BooleanProperty(False)
    mock_active = BooleanProperty(False)  # True wenn Mock GPS aktiv ist

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.last_lat = None
        self.last_lon = None
        self.last_time = None
        self.mock_event = None  # Clock event oder None
        self.track_line = None
        self.start_marker = None
        self.end_marker = None
        self.track_saved = True  # Track ist am Anfang "gespeichert"

    def start_tracking(self):
        if self.gps_started or self.mock_active:
            self.status_text = "Tracking läuft bereits"
            return
        self.reset_tracking()
        self.track_saved = False
        self._start_gps()
        self.ids.pause_resume_btn.text = "⏸ Pause"
        self.ids.pause_resume_btn.disabled = False
        self.ids.stop_btn.disabled = False
        self.ids.reset_btn.disabled = False

    def _start_gps(self):
        if sys.platform == "darwin":
            self.status_text = "macOS erkannt – Mock GPS aktiviert"
            if not self.mock_event:
                self.mock_event = Clock.schedule_interval(self.mock_gps_update, 5)
                self.mock_active = True
                print("Mock GPS gestartet")
            self.gps_started = True
        else:
            if gps:
                try:
                    gps.configure(on_location=self.on_location)
                    gps.start()
                    self.gps_started = True
                    self.mock_active = False
                    self.status_text = "GPS gestartet"
                except NotImplementedError:
                    self.status_text = "GPS nicht verfügbar"
                except Exception as e:
                    self.status_text = f"Fehler beim Starten von GPS: {e}"
            else:
                self.status_text = "Plyer GPS-Modul nicht gefunden"
                self.mock_active = False

    def pause_or_resume_tracking(self):
        if self.gps_started or self.mock_active:
            self._pause_gps()
            self.ids.pause_resume_btn.text = "▶ Fortsetzen"
        else:
            self._start_gps()
            self.ids.pause_resume_btn.text = "⏸ Pause"

    def _pause_gps(self):
        if sys.platform == "darwin":
            if self.mock_event:
                self.mock_event.cancel()
                self.mock_event = None
                self.mock_active = False
                self.status_text = "Mock GPS pausiert"
                print("Mock GPS pausiert")
            self.gps_started = False
        else:
            if self.gps_started and gps:
                try:
                    gps.stop()
                    self.gps_started = False
                    self.status_text = "GPS pausiert"
                    print("GPS pausiert")
                except Exception as e:
                    self.status_text = f"Fehler beim Pausieren von GPS: {e}"

    def stop_tracking(self):
        self._pause_gps()
        if not self.track_saved and self.track_points:
            self.status_text = "Achtung: Track wurde noch nicht gespeichert!"
        else:
            self.reset_tracking()
            self.ids.pause_resume_btn.text = "⏸ Pause"
            self.ids.pause_resume_btn.disabled = True
            self.ids.stop_btn.disabled = True
            self.ids.reset_btn.disabled = True
            self.status_text = "Tracking gestoppt und zurückgesetzt"

    def reset_tracking(self):
        self.distance = 0.0
        self.speed = 0.0
        self.last_lat = None
        self.last_lon = None
        self.last_time = None
        self.track_points = []
        self.track_saved = True
        self.status_text = "Tracking zurückgesetzt"

        self.ids.distance_label.text = "Distanz: 0.0 km"
        self.ids.coords_label.text = "Latitude: - , Longitude: -"
        self.ids.speed_label.text = "Geschwindigkeit: 0.0 km/h"

        mapview = self.ids.mapview
        mapview.center_on(52.5200, 13.4050)
        mapview.zoom = 12

        if self.start_marker:
            mapview.remove_widget(self.start_marker)
            self.start_marker = None
        if self.end_marker:
            mapview.remove_widget(self.end_marker)
            self.end_marker = None

        if self.track_line:
            mapview.canvas.remove(self.track_line)
            self.track_line = None

        print("Tracking und Marker zurückgesetzt")

    def on_location(self, **kwargs):
        lat = float(kwargs.get("lat", 0))
        lon = float(kwargs.get("lon", 0))
        now = datetime.now()

        self.ids.coords_label.text = f"Latitude: {lat:.5f}, Longitude: {lon:.5f}"

        if self.last_lat is not None and self.last_lon is not None and self.last_time is not None:
            dist = ((lat - self.last_lat) ** 2 + (lon - self.last_lon) ** 2) ** 0.5 * 111
            self.distance += dist
            self.ids.distance_label.text = f"Distanz: {self.distance:.2f} km"

            delta_t = (now - self.last_time).total_seconds()
            if delta_t > 0:
                self.speed = dist / (delta_t / 3600)
                self.ids.speed_label.text = f"Geschwindigkeit: {self.speed:.2f} km/h"

        self.last_lat = lat
        self.last_lon = lon
        self.last_time = now

        mapview = self.ids.mapview

        self.track_points.append((lat, lon))
        self.track_saved = False

        if not self.start_marker:
            self.start_marker = MapMarkerPopup(lat=lat, lon=lon)
            mapview.add_widget(self.start_marker)

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

        if self.track_line:
            mapview.canvas.remove(self.track_line)

        with mapview.canvas:
            Color(1, 0, 0, 1)
            self.track_line = Line(points=points, width=2)

    def save_track(self):
        if not self.track_points:
            self.status_text = "Kein Track zum Speichern vorhanden."
            return

        # Speicherordner "tracks" anlegen, falls nicht existiert
        folder = os.path.join(os.getcwd(), "tracks")
        os.makedirs(folder, exist_ok=True)

        data = {
            "date": datetime.now().isoformat(),
            "track_points": self.track_points,
            "distance_km": self.distance,
        }
        filename = f"track_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(folder, filename)
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            self.status_text = f"Track gespeichert: {filepath}"
            self.track_saved = True
            self.show_popup("Erfolg", f"Track gespeichert:\n{filepath}")
        except Exception as e:
            self.status_text = f"Fehler beim Speichern: {e}"
            self.show_popup("Fehler", f"Fehler beim Speichern:\n{e}")

    def open_filechooser(self):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.filechooser = FileChooserListView(filters=['*.json'])
        # Fester Ordner "tracks"
        folder = os.path.join(os.getcwd(), "tracks")
        os.makedirs(folder, exist_ok=True)
        self.filechooser.path = folder

        content.add_widget(self.filechooser)

        btn_layout = BoxLayout(size_hint_y=None, height='40dp', spacing=10)
        btn_load = Button(text='Laden', size_hint_x=0.5)
        btn_cancel = Button(text='Abbrechen', size_hint_x=0.5)
        btn_layout.add_widget(btn_load)
        btn_layout.add_widget(btn_cancel)
        content.add_widget(btn_layout)

        self.popup = Popup(title='Track Datei wählen',
                           content=content,
                           size_hint=(0.9, 0.9))

        btn_load.bind(on_release=self.load_from_filechooser)
        btn_cancel.bind(on_release=self.popup.dismiss)

        self.popup.open()

    def load_from_filechooser(self, instance):
        selected = self.filechooser.selection
        if selected:
            filepath = selected[0]
            self.load_track(filepath)
        self.popup.dismiss()

    def load_track(self, filepath=None):
        if not filepath:
            self.status_text = "Kein Pfad zum Laden angegeben."
            return

        if not os.path.isfile(filepath):
            self.status_text = "Datei existiert nicht."
            self.show_popup("Fehler", "Datei existiert nicht.")
            return

        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                points = data.get('track_points', [])
                if not points:
                    self.status_text = "Keine Track-Punkte gefunden."
                    self.show_popup("Fehler", "Keine Track-Punkte gefunden.")
                    return

                self.reset_tracking()

                mapview = self.ids.mapview

                for lat, lon in points:
                    self.track_points.append((lat, lon))

                lat_start, lon_start = self.track_points[0]
                self.start_marker = MapMarkerPopup(lat=lat_start, lon=lon_start)
                mapview.add_widget(self.start_marker)

                lat_end, lon_end = self.track_points[-1]
                self.end_marker = MapMarkerPopup(lat=lat_end, lon=lon_end)
                mapview.add_widget(self.end_marker)

                mapview.center_on(lat_end, lon_end)
                self.draw_track_line()

                self.status_text = f"Track geladen: {filepath}"
                self.track_saved = True
                self.show_popup("Erfolg", f"Track geladen:\n{filepath}")
        except Exception as e:
            self.status_text = f"Fehler beim Laden: {e}"
            self.show_popup("Fehler", f"Fehler beim Laden:\n{e}")

    def mock_gps_update(self, dt):
        import random
        lat = 52.5200 + random.uniform(-0.001, 0.001)
        lon = 13.4050 + random.uniform(-0.001, 0.001)
        self.on_location(lat=lat, lon=lon)

    def show_popup(self, title, message):
        popup_content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        popup_label = Button(text=message, size_hint_y=None, height=100, background_color=(0,0,0,0), disabled=True)
        btn_close = Button(text="Schließen", size_hint_y=None, height='40dp')
        popup_content.add_widget(popup_label)
        popup_content.add_widget(btn_close)
        popup = Popup(title=title, content=popup_content, size_hint=(0.7, 0.4))
        btn_close.bind(on_release=popup.dismiss)
        popup.open()


class BikeApp(App):
    def build(self):
        return MainLayout()


if __name__ == "__main__":
    BikeApp().run()
