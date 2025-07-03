Bike Tracker App mit Python und Kivy

Beschreibung

Die Bike Tracker App ist eine Fahrrad-Tracking-Anwendung, die mit Kivy entwickelt wurde. Sie ermöglicht es, während einer Fahrradtour GPS-Positionen zu erfassen, die gefahrene Strecke auf einer Karte anzuzeigen und wichtige Fahrdaten wie zurückgelegte Distanz, Geschwindigkeit und Fahrtdauer in Echtzeit zu verfolgen.

Die App bietet zusätzlich Funktionen zum Speichern und Laden von Tracks als JSON-Dateien sowie eine Mock-GPS-Option für Systeme ohne GPS (z.B. macOS).
Funktionen

    Live-Tracking: Erfassung der aktuellen GPS-Position und Anzeige auf einer interaktiven Karte.

    Streckenanzeige: Darstellung der gefahrenen Route als rote Linie auf der Karte.

    Fahrtdaten: Echtzeit-Anzeige von Distanz (km), Geschwindigkeit (km/h) und Fahrtdauer (hh:mm:ss).

    Track-Speicherung: Speichern der Tour als JSON-Datei inklusive Zeitstempel, Koordinaten, Distanz und Dauer.

    Track-Laden: Auswahl und Laden zuvor gespeicherter Tracks zur Ansicht und Analyse.

    Mock-GPS: Simulierte Positionsupdates für Systeme ohne GPS, ideal zur Entwicklung und Tests.

    Pause/Fortsetzen: Tracking pausieren und fortsetzen, ohne den aktuellen Track zu verlieren.

    Reset: Zurücksetzen des aktuellen Tracks und aller Anzeigen.

Installation & Nutzung

    Voraussetzungen:

        Python 3.x

        Kivy Framework

        kivy_garden.mapview Modul (für Kartenanzeige)

        Optional: plyer für GPS-Zugriff (vor allem auf Mobilgeräten)

    Installation der Abhängigkeiten:

pip install kivy kivy_garden.mapview plyer

Starten der App:

    python bike_tracker_app.py

    Hinweise:

        Auf macOS wird standardmäßig das Mock-GPS genutzt, da dort keine native GPS-Unterstützung vorhanden ist.

        Gespeicherte Tracks liegen im Verzeichnis tracks/ als JSON-Dateien.

        Die App benötigt GPS-Berechtigungen auf Mobilgeräten.

Aufbau des Codes

    MainLayout (Kivy BoxLayout): Enthält die Hauptlogik und Benutzeroberfläche für Tracking, Anzeige und Steuerung.

    GPS-Verwaltung: Integration von plyer.gps für Standortdaten, alternativ Mock-Daten auf macOS.

    Kartenanzeige: Nutzt kivy_garden.mapview für interaktive Karten und Marker.

    Tracking-Daten: Speicherung und Berechnung von Distanz, Geschwindigkeit und Dauer.

    Dateimanagement: Speichern und Laden von Tracks als JSON.

    UI-Komponenten: Buttons, Labels, Popups für Benutzerinteraktionen.


Bike Tracker App with Python and Kivy

Description

The Bike Tracker App is a bicycle tracking application developed using Kivy. It enables recording GPS positions during a bike ride, displaying the traveled route on a map, and tracking key ride data such as distance, speed, and duration in real time.

The app also offers features for saving and loading tracks as JSON files and includes a mock GPS option for systems without GPS (e.g., macOS).
Features

    Live Tracking: Capture current GPS location and display it on an interactive map.

    Route Display: Visualize the traveled route as a red line on the map.

    Ride Data: Real-time display of distance (km), speed (km/h), and duration (hh:mm:ss).

    Track Saving: Save the ride as a JSON file including timestamp, coordinates, distance, and duration.

    Track Loading: Select and load previously saved tracks for viewing and analysis.

    Mock GPS: Simulated position updates for systems without GPS, ideal for development and testing.

    Pause/Resume: Pause and resume tracking without losing the current track.

    Reset: Reset the current track and all displays.

Installation & Usage

    Requirements:

        Python 3.x

        Kivy framework

        kivy_garden.mapview module (for map display)

        Optional: plyer for GPS access (especially on mobile devices)

    Install dependencies:

pip install kivy kivy_garden.mapview plyer

Run the app:

    python bike_tracker_app.py

    Notes:

        On macOS, mock GPS is used by default since native GPS support is missing.

        Saved tracks are stored as JSON files in the tracks/ directory.

        The app requires GPS permissions on mobile devices.

Code Structure

    MainLayout (Kivy BoxLayout): Contains the main logic and UI for tracking, display, and control.

    GPS Management: Integration with plyer.gps for location data, with mock data fallback on macOS.

    Map Display: Uses kivy_garden.mapview for interactive maps and markers.

    Tracking Data: Stores and calculates distance, speed, and duration.

    File Management: Saving and loading tracks as JSON files.

    UI Components: Buttons, labels, popups for user interactions.