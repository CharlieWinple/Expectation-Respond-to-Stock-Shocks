"""Local figure from verified platform aggregates; does not reconstruct microdata."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'outputs/platform_runs/sme_owner_formal/run_11021235/verified/sme_owner_formal_11021235.json'
OUT = ROOT / 'docs/notes/figures'

def main():
    data = json.loads(SOURCE.read_text(encoding='utf-8'))
    rows = {r['variable']: r for r in data['distributions'] if r['scope'] == 'BASE_positive'}
    keys = ['p1', 'p10', 'p50', 'p90', 'p99']
    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({'font.family': 'DejaVu Serif', 'font.size': 10,
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'pdf.fonttype': 42})
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 4.0))
    gain = [rows['passive_gain'][k] * 10000 for k in keys]
    holding = [rows['portfolio_size_raw'][k] for k in keys]
    labels = [['-3,755', '-31.55', '0.01219', '102.9', '3,933'],
              ['0.5952', '1.2', '111.1', '40,550', '498,700']]
    for ax, values, title, color, point_labels in zip(
            axes, [gain, holding], ['A. Passive gain', 'B. Initial holdings'],
            ['#27638b', '#9a5529'], labels):
        ax.scatter(values, range(5), s=42, color=color, zorder=3)
        ax.set_yticks(range(5), ['P1', 'P10', 'Median', 'P90', 'P99'])
        ax.set_ylim(-.5, 4.65)
        ax.grid(axis='y', color='#e2e2e2', linewidth=.7)
        ax.set_title(title, loc='left', fontsize=12, pad=14)
        for y, value, label in zip(range(5), values, point_labels):
            ax.annotate(label, (value, y), xytext=(0, 9), textcoords='offset points',
                        ha='center', va='bottom', fontsize=9, color=color)
        ax.xaxis.set_major_formatter(FuncFormatter(lambda v, pos: f'{v:,.0f}' if abs(v)>=1 else f'{v:g}'))
    axes[0].set_xscale('symlog', linthresh=1, linscale=1)
    axes[0].set_xlim(-15000, 15000)
    axes[0].set_xticks([-1000, -10, 0, 10, 1000])
    axes[0].axvline(0, color='#bcbcbc', linewidth=.8, zorder=0)
    axes[0].set_xlabel('RMB; symmetric log scale, linear within +/-1')
    axes[1].set_xscale('log')
    axes[1].set_xlim(.15, 2500000)
    axes[1].set_xticks([1, 100, 10000, 1000000])
    axes[1].set_xlabel('RMB; log scale')
    fig.subplots_adjust(left=.09, right=.97, top=.86, bottom=.22, wspace=.30)
    fig.text(.09, .04, 'Positive-holder complete-control base: N = 12,153 owner-wave observations.\n'
             'Dots are reported quantiles, not frequencies or a fitted density.', fontsize=9, color='#444444')
    fig.savefig(OUT/'owner_gain_holding_quantiles.pdf', bbox_inches='tight')
    fig.savefig(OUT/'owner_gain_holding_quantiles.png', dpi=180, bbox_inches='tight')
    plt.close(fig)

if __name__ == '__main__':
    main()
