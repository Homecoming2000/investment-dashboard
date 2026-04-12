# Technische Dokumentation

Diese Dokumentation beschreibt den Aufbau des Investment Dashboards auf
Modul-Ebene. Zielgruppe: Entwickler, die den Code erweitern oder
reviewen wollen.

---

## Systemübersicht

Das Dashboard ist eine dreischichtige Anwendung:

1. **Datenschicht** – CSV-Dateien als Persistenz, yfinance als externe
   Live-Quelle
2. **Logikschicht** – Module für Berechnung, Aggregation und Historie
3. **Präsentationsschicht** – Streamlit-Seiten mit Charts und Tabellen

```
┌─────────────────────────────────────────────────────────┐
│  Streamlit UI (app.py + pages/)                         │
│  Metriken, Tabellen, Charts, Interaktionen              │
└───────────────────────┬─────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼─────┐ ┌───────▼──────┐ ┌─────▼────────┐
│ Performance │ │   Dividend   │ │     Logo     │
│   Tracker   │ │   Tracker    │ │   Mapping    │
└───────┬─────┘ └───────┬──────┘ └──────────────┘
        │               │
        │       ┌───────┴────────┐
        │       │                │
┌───────▼───────▼────────┐ ┌─────▼──────────┐
│  Portfolio.csv         │ │  yfinance API  │
│  portfolio_history.csv │ │  (extern)      │
└────────────────────────┘ └────────────────┘
```

---

## Modulübersicht

### app.py

Einstiegspunkt und Hauptseite. Zuständig für:

- Passwortprüfung (im Demo-Modus deaktiviert)
- Laden der Portfoliodaten
- Abruf der Live-Preise via `get_price()`
- Berechnung der Gesamtmetriken (Investment, aktueller Wert, Gewinn)
- Rendering der Tabelle mit Logo-Spalte
- Anzeige der Top/Worst Performer

Der Einstiegspunkt ruft `PerformanceTracker.log_daily_value()` bei
jedem Seitenaufruf auf, wodurch die Historie automatisch fortgeschrieben
wird.

### pages/1_Analyse.py

Unterseite für Portfolio-Analyse. Enthält:

- Performance-Chart mit Zeitraumauswahl
- Asset-Klassen-Verteilung (Pie Chart)
- Sektorverteilung (Pie Chart)
- Geografische Verteilung (Pie Chart)

Alle Pie Charts nutzen Hover-Details, die die einzelnen Ticker innerhalb
einer Kategorie auflisten. Die Implementierung geht über ein
vorberechnetes Hover-HTML pro Segment, das Plotly über `customdata`
eingespielt wird.

### pages/2_Dividenden.py

Unterseite für Ausschüttungsanalyse. Enthält:

- Brutto/Netto-Metriken unter Berücksichtigung der deutschen
  Abgeltungssteuer (26,375%)
- Anstehende Zahlungen der nächsten 90 Tage
- Top 5 Dividenden-Zahler nach jährlicher Ausschüttung

### performance_tracker.py

Kapselt die historische Wertentwicklung:

- `log_daily_value()`: Schreibt täglich einen Datenpunkt in die Historie.
  Pro Tag wird maximal ein Eintrag gespeichert – mehrfache Aufrufe am
  selben Tag überschreiben den bestehenden Wert.
- `get_performance_data()`: Liefert einen gefilterten Datensatz für den
  gewünschten Zeitraum, inklusive Statistiken (Min, Max, Durchschnitt,
  Volatilität).
- `create_performance_chart()`: Rendert den Verlauf als Plotly-Chart mit
  farbigem Flächenverlauf.

Die Historie liegt pro Modus in einer eigenen Datei:
`portfolio_history.csv` für den produktiven Modus,
`portfolio_history.demo.csv` für den Demo-Modus.

### dividend_tracker.py

Berechnungen rund um Ausschüttungen:

- `get_dividend_payers()`: Filtert Positionen mit hinterlegten
  Dividenden-Informationen.
- `calculate_annual_dividend()`: Rechnet Frequenz (Annual, SemiAnnual,
  Quarterly, Monthly) auf Jahresbasis hoch.
- `calculate_yield_on_cost()`: Ermittelt die Rendite auf den
  Einstandspreis, nicht auf den aktuellen Kurs.
- `get_upcoming_payments()`: Listet anstehende Auszahlungen im
  angegebenen Zeitfenster.
- `get_top_dividend_payers()`: Ranking nach jährlicher Ausschüttung in
  EUR.

### logo_mapping.py

Übersetzt Ticker in Logo-URLs. Zwei Sonderfälle:

1. Tickern in `USE_FALLBACK_DIRECTLY` (z.B. physisches Gold) wird direkt
   das Fallback-Icon zugeordnet, da für diese Einträge ohnehin kein
   sinnvolles Logo existiert.
2. Tickern ohne Eintrag in `TICKER_DOMAINS` wird ebenfalls das Fallback
   geliefert.

Zusätzlich liefert `get_region()` die geografische Zuordnung anhand des
Ticker-Suffix (`.DE` → Europa, `.L` → Europa, `.AS` → Europa, kein
Suffix → Nordamerika, etc.).

### styles.py

Zwei Aufgaben:

1. `get_custom_css(dark_mode)`: Liefert den CSS-String für das jeweilige
   Theme.
2. `show_demo_banner(compact)`: Rendert den Demo-Hinweis in zwei
   Varianten. Die große Version steht auf der Hauptseite, die kompakte
   Version auf den Unterseiten.

---

## Datenfluss

### Beim Seitenaufruf (Hauptseite)

1. `main()` wird von Streamlit aufgerufen
2. `check_password()` prüft, ob Zugriff erlaubt ist (im Demo-Modus
   immer)
3. `load_portfolio(PORTFOLIO_FILE)` lädt die CSV – entweder echt oder
   Demo
4. Für jeden Ticker wird `get_price(ticker)` aufgerufen
5. `get_price()` prüft den Cache (TTL 300s), ansonsten Yahoo-API-Call
6. Bei Nicht-EUR-Kursen wird `get_exchange_rate()` aufgerufen (Cache
   TTL 1800s)
7. Die Metriken werden berechnet und das Dashboard gerendert
8. `log_daily_value()` schreibt den aktuellen Wert in die Historie

### Bei der Analyse-Seite

1. Die Historie wird aus der CSV geladen
2. Aus den hinterlegten Einträgen wird ein Plotly-Chart erstellt
3. Die Min/Max/Durchschnitt-Werte werden aus der aktuellen Auswahl
   berechnet
4. Die drei Pie Charts werden aus den aktuellen Live-Preisen und der
   Portfolio-CSV erzeugt

---

## Caching-Strategie

| Funktion | TTL | Begründung |
|----------|-----|------------|
| `get_price` | 300s | Preise ändern sich kontinuierlich, 5 Minuten sind ein guter Kompromiss zwischen Aktualität und API-Last |
| `get_exchange_rate` | 1800s | Wechselkurse sind träger, 30 Minuten reichen |
| `load_portfolio` | 3600s | Die CSV ändert sich selten, 1 Stunde ist sicher |

Bei Änderung der CSV: Cache manuell leeren (oben rechts im
Streamlit-Interface) oder den Streamlit-Prozess neu starten.

---

## Sicherheitsaspekte

**Trennung von Daten und Code**: Echte Portfoliodaten liegen in
separaten Dateien, die per `.gitignore` vom Repository ausgeschlossen
sind. Die Beispieldaten haben eigene Dateinamen mit `.demo.csv`-Suffix.

**Passwortschutz**: Der produktive Modus erfordert ein Passwort aus
`.streamlit/secrets.toml`. Die Datei ist ebenfalls in `.gitignore`.

**Session-Timeout**: Eine Session läuft automatisch nach 8 Minuten
Inaktivität ab, danach ist eine neue Authentifizierung nötig.

**Fail-Safe**: Falls die produktive `Portfolio.csv` nicht existiert
(z.B. bei Cloud-Deployment oder frischem Clone), wechselt das Dashboard
automatisch in den Demo-Modus. Das verhindert Abstürze und stellt sicher,
dass keine leeren Fehlermeldungen angezeigt werden.

**Demo-Isolation**: Beim Deployment auf Streamlit Cloud wird die
Umgebungsvariable `DEMO_MODE=true` gesetzt. Selbst wenn diese fehlen
würde, greift der Fail-Safe.

---

## Deployment

### Lokal

```bash
streamlit run app.py
```

Das Dashboard ist danach unter `http://localhost:8501` erreichbar.

### Streamlit Cloud

1. Repository auf GitHub pushen
2. Auf streamlit.io einloggen (GitHub-Auth)
3. Repository auswählen, `app.py` als Entry Point
4. Unter „Advanced settings → Secrets" hinzufügen:
```toml
   DEMO_MODE = "true"
```
5. Deployen

Die Cloud-Version läuft automatisch im Demo-Modus.

---

## Troubleshooting

**"possibly delisted; no price data found"**: Der Ticker existiert bei
Yahoo nicht mehr. Entweder Ticker in der CSV korrigieren oder Eintrag
entfernen.

**Logos werden nicht angezeigt**: Browser-Werbeblocker deaktivieren oder
im Inkognito-Modus testen. Google Favicons werden manchmal von
Adblockern geblockt.

**Historie wird nicht erstellt**: Prüfen, ob der Ordner Schreibrechte
hat. Die Datei `portfolio_history.csv` wird automatisch angelegt, wenn
sie fehlt.

**Dark Mode wirkt nicht**: CSS wird nur beim initialen Rendering
gesetzt. Ein Toggle des Dark-Mode-Schalters erfordert einen Rerun der
Seite (automatisch durch Streamlit).

---

## Erweiterung: Neue Asset-Klasse

Um eine neue Asset-Klasse (z.B. Immobilien-Fonds) zu unterstützen:

1. In der CSV einen neuen `Type`-Wert eintragen (z.B. `REIT`)
2. Falls spezielle Preisabfrage nötig: In `get_price()` einen
   zusätzlichen Branch einbauen
3. Falls gewünscht: Eigene Logo-Domain in `logo_mapping.py` eintragen
4. Die Pie Charts greifen den neuen Typ automatisch auf, keine weiteren
   Änderungen nötig

---

## Erweiterung: Neue Seite

1. Datei in `pages/` anlegen (z.B. `3_Benchmark.py`)
2. Standard-Imports übernehmen (`os`, `streamlit`, eigene Module)
3. `DEMO_MODE`-Check und `PORTFOLIO_FILE`-Auswahl einbauen
4. `show_demo_banner(compact=True)` falls im Demo-Modus
5. Streamlit erstellt den Eintrag in der Sidebar automatisch aus dem
   Dateinamen