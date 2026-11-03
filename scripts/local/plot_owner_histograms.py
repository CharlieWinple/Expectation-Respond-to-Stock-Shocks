"""Render Cell 11's verified histogram table: python plot_owner_histograms.py bins.csv"""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def render(source):
    table = pd.read_csv(source)
    destination = source.parent.parent / "figures"
    destination.mkdir(exist_ok=True)
    panels = {}
    for variable in ("holding", "gain"):
        log_scale = "log10_RMB" if variable == "holding" else "signed_log10_1p"
        for scale in ("RMB", log_scale):
            key = f"{variable}_{scale}"
            rows = table.loc[table.panel == key].sort_values("bin")
            lower, upper, counts = (rows[c].to_numpy() for c in ("lower", "upper", "N"))
            if (len(rows) not in (1, 20) or list(rows.bin) != list(range(1, len(rows)+1))
                    or not np.isfinite([lower, upper, counts]).all()
                    or not np.all(upper > lower) or not np.array_equal(lower[1:], upper[:-1])
                    or not np.all((counts >= 0) & (counts == np.floor(counts))) or counts.sum() <= 0):
                raise ValueError(f"Check the transcribed bin boundaries and counts for {key}")
            panels[variable, scale] = (lower, upper, counts)
        if panels[variable, "RMB"][2].sum() != panels[variable, log_scale][2].sum():
            raise ValueError(f"Panel totals disagree for {variable}")
    for variable in ("holding", "gain"):
        fig, axes = plt.subplots(1, 2, figsize=(10, 4), layout="constrained")
        for ax, ((_, scale), (lo, hi, n)) in zip(axes, (p for p in panels.items() if p[0][0] == variable)):
            if scale == "RMB":
                lo, hi = lo/10000, hi/10000
            ax.bar(lo, n, width=hi-lo, align="edge", color="#286080", edgecolor="white", linewidth=.4)
            ax.set(xlabel={"RMB": "Amount (10,000 RMB)", "log10_RMB": "log10(holdings in RMB)",
                           "signed_log10_1p": "Signed log10(1 + |gain in RMB|)"}[scale],
                   ylabel="Owner-wave observations")
        fig.suptitle(f"{variable.capitalize()} among positive holders (N = {int(n.sum()):,})")
        for ext in ("pdf", "png"):
            fig.savefig(destination / f"owner_{variable}_histogram.{ext}", dpi=300)
        plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    render(parser.parse_args().source)
