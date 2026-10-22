import matplotlib.pyplot as plt
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
results_file = ROOT / "report_assets" / "comparative_benchmark_results.csv"

rows = []
with open(results_file) as f:
    reader = csv.DictReader(f)
    rows = list(reader)

stuck_rows = [r for r in rows if "Stuck" in r["scenario"]]
methods = ["TIMEOUT(cutoff=10)", "REPEAT_COUNTER", "LBA_GUARDRAIL"]
scenarios = ["StuckAgent(period=1)", "StuckAgent(period=3)", "StuckAgent(period=5)"]

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# Left: detection success (1 = detected, 0 = failed to detect)
ax = axes[0]
active_halts = {"TIMEOUT_HALT", "REPEAT_COUNTER_HALT", "LBA_HALT"}
x = range(len(scenarios))
width = 0.25
colors = {"TIMEOUT(cutoff=10)": "#f59e0b", "REPEAT_COUNTER": "#ef4444", "LBA_GUARDRAIL": "#10b981"}

for i, method in enumerate(methods):
    vals = []
    for sc in scenarios:
        match = [r for r in stuck_rows if r["scenario"] == sc and r["method"] == method][0]
        vals.append(1 if match["result"] in active_halts else 0)
    offset = (i - 1) * width
    ax.bar([xi + offset for xi in x], vals, width, label=method, color=colors[method])

ax.set_xticks(list(x))
ax.set_xticklabels(["period=1", "period=3", "period=5"])
ax.set_ylabel("Loop actually detected? (1=yes, 0=never)")
ax.set_title("Detection success by loop period")
ax.set_ylim(0, 1.3)
ax.legend(fontsize=8)

# Right: steps taken (only when detected)
ax = axes[1]
for i, method in enumerate(methods):
    vals = []
    for sc in scenarios:
        match = [r for r in stuck_rows if r["scenario"] == sc and r["method"] == method][0]
        vals.append(int(match["steps"]) if match["result"] in active_halts else None)
    xs = [xi + (i - 1) * width for xi, v in zip(x, vals) if v is not None]
    ys = [v for v in vals if v is not None]
    ax.bar(xs, ys, width, label=method, color=colors[method])

ax.set_xticks(list(x))
ax.set_xticklabels(["period=1", "period=3", "period=5"])
ax.set_ylabel("Steps taken to detect (lower = less wasted compute)")
ax.set_title("Cost of detection (only where detection succeeded)")
ax.legend(fontsize=8)

plt.tight_layout()
out_png = ROOT / "report_assets" / "figures" / "comparative_chart.png"
out_png.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(out_png, dpi=200, bbox_inches="tight", facecolor="white")
print(f"saved: {out_png}")
