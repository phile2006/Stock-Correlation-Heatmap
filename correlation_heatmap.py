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

def download_prices(args: argparse.Namespace) -> pd.DataFrame:
    """Lädt Schlusskurse (dividenden-/splitbereinigt) für alle Ticker."""
    kwargs = dict(interval=args.interval, auto_adjust=True, progress=False)
    if args.start:
        data = yf.download(args.tickers, start=args.start, end=args.end, **kwargs)
    else:
        data = yf.download(args.tickers, period=args.period, **kwargs)

    if data.empty:
        sys.exit("Fehler: keine Kursdaten erhalten – Ticker/Zeitraum prüfen.")

    close = data["Close"]
    if isinstance(close, pd.Series):  # nur ein Ticker
        close = close.to_frame(args.tickers[0])

    # Ticker ohne Daten aussortieren (z.B. Tippfehler im Symbol)
    dead = [t for t in close.columns if close[t].dropna().empty]
    if dead:
        print(f"Warnung: keine Daten für {', '.join(dead)} – wird übersprungen.")
        close = close.drop(columns=dead)
    if close.shape[1] < 2:
        sys.exit("Fehler: mindestens 2 Ticker mit Daten nötig.")

    # Warnen, wenn ein Ticker deutlich später beginnt (verkürzt die gemeinsame Historie)
    starts = {t: close[t].first_valid_index() for t in close.columns}
    latest_start = max(starts.values())
    common_start = min(starts.values())
    if (latest_start - common_start).days > 30:
        late = [t for t, s in starts.items() if s == latest_start]
        print(f"Hinweis: {', '.join(late)} beginnt erst am "
              f"{latest_start.date()} – gemeinsame Historie entsprechend kürzer.")

    return close.dropna()

def compute_correlation(close: pd.DataFrame, args: argparse.Namespace) -> tuple[pd.DataFrame, int]:
    """Berechnet Renditen und deren Korrelationsmatrix."""
    if args.returns == "log":
        returns = np.log(close / close.shift(1)).dropna()
    else:
        returns = close.pct_change().dropna()
    if len(returns) < 20:
        print(f"Warnung: nur {len(returns)} gemeinsame Beobachtungen – "
              "Korrelationen sind statistisch wenig belastbar.")
    return returns.corr(method=args.method), len(returns)



def cluster_order(corr: pd.DataFrame) -> list[str]:
    """Ordnet Ticker per hierarchischem Clustering, damit korrelierte
    Blöcke in der Heatmap nebeneinander liegen."""
    from scipy.cluster.hierarchy import leaves_list, linkage
    from scipy.spatial.distance import squareform

    dist = 1.0 - corr.values
    np.fill_diagonal(dist, 0.0)
    dist = (dist + dist.T) / 2  # numerische Symmetrie erzwingen
    link = linkage(squareform(dist, checks=False), method="average")
    return [corr.columns[i] for i in leaves_list(link)]



def plot_heatmap(corr: pd.DataFrame, n_obs: int, args: argparse.Namespace) -> None:
    """Zeichnet die Heatmap und speichert sie als PNG."""
    n = len(corr)
    size = max(7.0, 0.65 * n + 2.5)
    fig, ax = plt.subplots(figsize=(size, size * 0.85))

    sns.heatmap(
        corr,
        ax=ax,
        cmap="RdBu_r",          # blau = negativ, rot = positiv
        vmin=-1.0, vmax=1.0, center=0.0,
        annot=not args.no_annot,
        fmt=".2f",
        annot_kws={"size": max(6, 11 - n // 4)},
        square=True,
        linewidths=0.5,
        linecolor="white",
        cbar_kws={"label": f"Korrelation ({args.method.capitalize()})", "shrink": 0.8},
    )
