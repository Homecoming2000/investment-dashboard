# Investment Dashboard

Lokales Portfolio-Dashboard zur Auswertung eines Multi-Asset-Portfolios
(Aktien, ETFs, Crypto, Edelmetalle). Kursdaten werden live von Yahoo
Finance geladen, Investmentbestände aus einer CSV eingelesen. Die
Visualisierung läuft über Streamlit.

Das Projekt ist als lokal gehostetes Tool konzipiert – die echten
Portfoliodaten verlassen den Rechner nicht. Für den öffentlichen Zugriff
existiert ein Demo-Modus, der mit fiktiven Beispieldaten arbeitet.

**Live-Demo:** [dashboard.streamlit.app](https://[URL_NACH_DEPLOYMENT])
*(Demo-Modus mit Beispieldaten, kein Zugriff auf reale Bestände)*

---

## Features

- **Live-Kursdaten** über yfinance, inkl. automatischer Währungsumrechnung
  (USD, GBP, DKK, SEK → EUR)
- **Multi-Asset-Unterstützung**: Aktien, ETFs, Kryptowährungen und
  Edelmetalle (Goldpreis wird über GLD-Proxy berechnet)
- **Performance-Tracker** mit historischer Wertentwicklung und wählbaren
  Zeiträumen (1D, 5D, 1M, 6M, YTD, 5Y, All)
- **Dividenden-Modul**: Brutto-/Netto-Berechnung nach deutscher
  Abgeltungssteuer, anstehende Zahlungen, Yield-on-Cost
- **Portfolio-Verteilung** nach Asset-Klasse, Sektor und Region
  (geografische Zuordnung automatisch über Ticker-Suffix)
- **Top/Worst Performer** für schnelle Übersicht der Bewegungen
- **Dark/Light Mode** und Logo-Anzeige via Google Favicons

---

## Technologie

| Komponente | Zweck |
|------------|-------|
| Python 3.10+ | Laufzeitumgebung |
| Streamlit | Web-UI und Server |
| Pandas | Datenverarbeitung |
| Plotly | Interaktive Charts |
| yfinance | Live-Kursdaten (Yahoo Finance API) |

---

## Projektstruktur
```
investment-dashboard/
├── app.py                       # Hauptseite: Metriken,  Tabelle, Performer
├── pages/
│   ├── 1_Analyse.py             # Performance-Chart und Verteilungen
│   └── 2_Dividenden.py          # Dividenden-Übersicht
├── performance_tracker.py       # Historien-Logging und Chart-Generierung
├── dividend_tracker.py          # Dividenden-Berechnung, Steuer, YoC
├── logo_mapping.py              # Ticker → Domain-Mapping für Logos
├── styles.py                    # CSS-Themes und Banner-Komponente
├── Portfolio.demo.csv           # Beispiel-Portfolio (im Repo)
├── portfolio_history.demo.csv   # Beispiel-Historie (im Repo)
├── Portfolio.csv                # Echtes Portfolio (NICHT im Repo)
├── portfolio_history.csv        # Echte Historie (NICHT im Repo)
├── requirements.txt             # Python-Abhängigkeiten
└── .gitignore                   # Ausschluss sensibler Daten
``` 

## Installation

Voraussetzungen: Python 3.10 oder neuer, Git.

```bash
git clone https://github.com/Homecoming2000/investment-dashboard.git
cd investment-dashboard

python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/macOS

pip install -r requirements.txt
```

---

## Nutzung

### Demo-Modus

Startet ohne Passwortschutz mit Beispieldaten. Geeignet zum Ausprobieren
oder für öffentliches Hosting.

**Windows (CMD):**
```bash
set DEMO_MODE=true
streamlit run app.py
```

**Linux/macOS:**
```bash
DEMO_MODE=true streamlit run app.py
```

### Produktiver Modus

Nutzt die echte `Portfolio.csv` und erfordert einen Passwortschutz über
Streamlit Secrets.

```bash
streamlit run app.py
```

Das Passwort wird in `.streamlit/secrets.toml` abgelegt:

```toml
APP_PASSWORD = "dein-passwort"
```

Die Datei ist in `.gitignore` und wird nicht versioniert.

---

## Eigenes Portfolio einrichten

Kopiere `Portfolio.demo.csv` zu `Portfolio.csv` und passe den Inhalt an.
Das Schema:

```csv
Ticker,Quantity,Type,Name,ISIN,BuyPrice,Sector,Dividend,DivMonth,DivFrequency
AAPL,10,Stock,APPLE INC,US0378331005,150.00,Informationstechnology,0.96,5,Quarterly
```

**Spalten:**

| Feld | Beschreibung |
|------|--------------|
| Ticker | Symbol laut Yahoo Finance (z.B. `AAPL`, `ALV.DE`, `BTC-USD`) |
| Quantity | Anzahl der Einheiten |
| Type | `Stock`, `ETF`, `Crypto`, `Commodity` |
| Name | Anzeigename |
| ISIN | Optional, zur Information |
| BuyPrice | Durchschnittlicher Einstandspreis in EUR |
| Sector | Kategorisierung für die Sektorverteilung |
| Dividend | Dividende pro Einheit (leer bei Nicht-Ausschüttern) |
| DivMonth | Monat der Auszahlung (1–12) |
| DivFrequency | `Annual`, `SemiAnnual`, `Quarterly`, `Monthly` |

---

## Architektur-Entscheidungen

**Demo-Modus über Umgebungsvariable**

Die Trennung zwischen produktiven und öffentlichen Daten läuft über die
Umgebungsvariable `DEMO_MODE`. Das Muster ist bewusst einfach gehalten:
Ein zentraler Check entscheidet zwischen `Portfolio.csv` und
`Portfolio.demo.csv`. Der Passwortschutz wird im Demo-Modus automatisch
deaktiviert, damit das Dashboard öffentlich zugänglich bleibt.

Der Grund für diese Architektur: Persönliche Finanzdaten dürfen unter
keinen Umständen versehentlich im öffentlichen Repository landen. Die
Umsetzung kombiniert drei Sicherheitsschichten – `.gitignore` für das
Repo, separate Dateien für die Daten, Umgebungsvariable für die Logik.

**Separation of Concerns**

Die Fachlogik ist auf eigene Module aufgeteilt: `performance_tracker.py`
für Historie und Charts, `dividend_tracker.py` für alles rund um
Ausschüttungen, `logo_mapping.py` für die Logo-URL-Generierung,
`styles.py` für CSS und wiederverwendbare UI-Komponenten. Die Hauptseite
und die Unterseiten orchestrieren, halten aber keine Geschäftslogik.

**Caching über Streamlit**

API-Calls sind teuer und ratenbegrenzt. Alle yfinance-Abfragen sind mit
`@st.cache_data` versehen: Preise für 5 Minuten, Wechselkurse für 30
Minuten, Portfoliostrukturen für 60 Minuten. Das reduziert die Last auf
die Yahoo-API erheblich und macht die UI spürbar schneller.

**Fallback für Logos**

Nicht jede Firma hat ein Logo bei der eingesetzten Logo-Quelle. Statt
kaputter Bilder zeigt das Mapping für bekannte Ausnahmen (Edelmetalle,
kleine Titel) direkt ein generisches Platzhalter-Icon.

---

## Bekannte Einschränkungen

- **yfinance ist nicht offiziell**: Die Library scraped Yahoo Finance.
  Bei größeren Änderungen auf Yahoo-Seite können einzelne Funktionen
  ausfallen. Produktivnutzung mit kritischen Daten wäre ein Fall für eine
  lizenzierte API wie Alpha Vantage oder Finnhub.
- **Dividenden-Termine manuell pflegen**: Yahoo liefert keine
  zuverlässigen Ex-Termine. Ausschüttungsmonat und -frequenz stehen
  daher in der CSV.
- **Gold-Kurse über GLD-Proxy**: Der Goldpreis wird aus dem SPDR Gold
  Shares ETF (GLD) abgeleitet. Kleine Abweichungen zum Spotpreis sind
  möglich.

---

## Ausbauideen

- Zweite Datenquelle als Fallback (z.B. Alpha Vantage)
- Docker-Image für reproducible Deployments
- Unit-Tests für die Berechnungslogik (Dividende, YoC, Währungsumrechnung)
- Konfiguration über zentrale `config.py` oder `.env`-Datei
- Benchmark-Vergleich (Portfolio vs. MSCI World)

---

## Lizenz

Freie Nutzung zu privaten und Bildungszwecken. Keine Gewähr für die
Richtigkeit der angezeigten Kursdaten.

---

## Kontakt

GitHub: [@Homecoming2000](https://github.com/Homecoming2000)