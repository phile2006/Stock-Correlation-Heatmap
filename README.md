# Stock-Correlation-Heatmap
Zeigt die Korrelation von verschiedenen Aktien als Heatmap. Stark korrelierte Paare bewegen sich verhältnismäßig gleich, niedrig oder negativ korrelierte Werte sind nützlich für die Diversifikation eines Portfolios.

Die Kursdaten werden kostenlos über [yfinance](https://github.com/ranaroussi/yfinance)
(Yahoo Finance) geladen, die Korrelationsmatrix wird als PNG gespeichert und
die extremsten Paare werden in der Konsole ausgegeben.

## Installation

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Verwendung

```sh
# Standard: US-Mega-Caps + ETFs (SPY, QQQ, GLD, TLT), 1 Jahr, Tagesdaten
.venv/bin/python correlation_heatmap.py

# Eigene Ticker (yfinance-Symbole; Xetra-Werte mit .DE-Suffix, z.B. SAP.DE)
.venv/bin/python correlation_heatmap.py --tickers AAPL MSFT SAP.DE SIE.DE --period 2y

# Fester Zeitraum, Wochendaten, Spearman-Korrelation
.venv/bin/python correlation_heatmap.py --start 2024-01-01 --end 2025-12-31 --interval 1wk --method spearman
```

## Optionen

| Option | Standard | Bedeutung |
|---|---|---|
| `--tickers` | US-Mega-Caps + ETFs | Liste der Ticker (yfinance-Symbole) |
| `--period` | `1y` | Zeitraum (`6mo`, `1y`, `2y`, `5y`, `max`, …) |
| `--start` / `--end` | — | Fester Datumsbereich `YYYY-MM-DD` (überschreibt `--period`) |
| `--interval` | `1d` | Datenintervall: `1d`, `1wk`, `1mo` |
| `--returns` | `log` | Renditeberechnung: `log` oder `simple` |
| `--method` | `pearson` | Korrelationsmethode: `pearson` oder `spearman` |
| `--sort` | `cluster` | Ticker-Sortierung: `cluster` (korrelierte Blöcke nebeneinander), `alpha`, `none` |
| `--output` | `heatmap.png` | Name der Ausgabedatei |
| `--no-annot` | — | Zahlenwerte in den Zellen ausblenden (bei vielen Tickern übersichtlicher) |

## Ausgabe

- **PNG-Heatmap** (`heatmap.png`): rot = positiv korreliert, blau = negativ,
  weiß = unkorreliert. Bei `--sort cluster` werden die Ticker per
  hierarchischem Clustering angeordnet, sodass korrelierte Gruppen als
  Blöcke sichtbar werden.
- **Konsole**: Anzahl der gemeinsamen Beobachtungen sowie die fünf am
  niedrigsten (Diversifikationskandidaten) und am höchsten korrelierten Paare.

## Hinweise zur Interpretation

- Die Korrelation wird auf **Renditen** berechnet, nicht auf Kursen —
  Kurskorrelationen wären durch gemeinsame Trends stark verzerrt.
- Log-Renditen (Standard) sind bei Tagesdaten praktisch identisch mit
  einfachen Renditen, aber additiv über die Zeit.
- Korrelationen sind **nicht stabil**: In Stressphasen steigen sie typischerweise
  an ("correlation goes to 1"). Ein kurzer Zeitraum (< ~60 Beobachtungen)
  liefert wenig belastbare Werte — das Skript warnt entsprechend.
- Bei Tickern unterschiedlicher Börsen (z.B. US + Xetra) überlappen sich die
  Handelstage nur teilweise; gemeinsame Feiertage reduzieren die Datenbasis,
  und unterschiedliche Handelszeiten können Korrelationen zu Tagesdaten
  leicht unterschätzen.

## Dateien

- `correlation_heatmap.py` — komplettes Tool (Daten laden, Korrelation, Heatmap)
- `requirements.txt` — Python-Abhängigkeiten
