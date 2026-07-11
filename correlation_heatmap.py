import argparse
import sys
import matplotlib
matplotlib.use("Agg")  # kein Fenster nötig, nur PNG-Ausgabe
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import yfinance as yf

# Standard-Universum: US-Mega-Caps + ETFs (SPY/QQQ = Aktienindizes,
# GLD = Gold, TLT = US-Staatsanleihen als Diversifikatoren)
DEFAULT_TICKERS = [
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA",
    "JPM", "XOM", "SPY", "QQQ", "GLD", "TLT",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Berechnet die Korrelation von Aktien-Renditen und "
                    "speichert sie als Heatmap (PNG).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--tickers", nargs="+", default=DEFAULT_TICKERS, help="Liste der Ticker (yfinance-Symbole, z.B. SAP.DE für Xetra)")
    p.add_argument("--period", default="1y", help="Zeitraum (z.B. 6mo, 1y, 2y, 5y, max); wird von --start/--end überschrieben")
    p.add_argument("--start", default=None, help="Startdatum YYYY-MM-DD")
    p.add_argument("--end", default=None, help="Enddatum YYYY-MM-DD")
    p.add_argument("--interval", default="1d", choices=["1d", "1wk", "1mo"], help="Datenintervall")
    p.add_argument("--returns", default="log", choices=["log", "simple"], help="Renditeberechnung: logarithmisch oder einfach")
    p.add_argument("--method", default="pearson", choices=["pearson", "spearman"], help="Korrelationsmethode")
    p.add_argument("--sort", default="cluster", choices=["cluster", "alpha", "none"], help="Sortierung der Ticker: hierarchisches Clustering, " "alphabetisch oder Eingabereihenfolge")
    p.add_argument("--output", default="heatmap.png", help="Ausgabedatei (PNG)")
    p.add_argument("--no-annot", action="store_true", help="Zahlenwerte in den Zellen ausblenden")
    return p.parse_args()
