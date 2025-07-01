from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock

class BikeTrackerApp(App):
    def build(self):
        self.tracking = False
        self.speed = 0
        self.distance = 0

        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        self.status_label = Label(text='Willkommen zum Bike Tracker!', font_size=24)
        self.speed_label = Label(text='Geschwindigkeit: 0 km/h', font_size=24)
        self.distance_label = Label(text='Distanz: 0 km', font_size=24)

        self.start_button = Button(text='Start', font_size=32)
        self.start_button.bind(on_press=self.start_tracking)

        self.stop_button = Button(text='Stop', font_size=32)
        self.stop_button.bind(on_press=self.stop_tracking)

        self.reset_button = Button(text='Reset', font_size=32)
        self.reset_button.bind(on_press=self.reset_tracking)

        layout.add_widget(self.status_label)
        layout.add_widget(self.speed_label)
        layout.add_widget(self.distance_label)
        layout.add_widget(self.start_button)
        layout.add_widget(self.stop_button)
        layout.add_widget(self.reset_button)

        return layout

    def start_tracking(self, instance):
        if not self.tracking:
            self.tracking = True
            self.status_label.text = 'Tracking läuft...'
            self.speed = 15
            Clock.schedule_interval(self.update_tracking, 1)

    def stop_tracking(self, instance):
        if self.tracking:
            self.tracking = False
            self.status_label.text = 'Tracking gestoppt.'
            self.speed = 0
            self.speed_label.text = 'Geschwindigkeit: 0 km/h'

    def reset_tracking(self, instance):
        self.tracking = False
        self.speed = 0
        self.distance = 0
        self.status_label.text = 'Tracking zurückgesetzt.'
        self.speed_label.text = 'Geschwindigkeit: 0 km/h'
        self.distance_label.text = 'Distanz: 0 km'
        Clock.unschedule(self.update_tracking)

    def update_tracking(self, dt):
        if self.tracking:
            self.distance += 0.004
            self.speed_label.text = f'Geschwindigkeit: {self.speed} km/h'
            self.distance_label.text = f'Distanz: {round(self.distance, 2)} km'
        else:
            return False

if __name__ == '__main__':
    BikeTrackerApp().run()
