import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

# Create a figure and axis
fig, ax = plt.subplots(figsize=(10, 5))
ax.axis('off')

# Function to draw a box
def draw_box(ax, x, y, width, height, text, facecolor='#eeeeee'):
    rect = patches.Rectangle((x, y), width, height, linewidth=2, edgecolor='black', facecolor=facecolor)
    ax.add_patch(rect)
    ax.text(x + width/2, y + height/2, text, ha='center', va='center', fontsize=12, fontweight='bold')

# Draw boxes
draw_box(ax, 0.5, 0.4, 2, 1, "Agent\n(LLM or Mock)", facecolor='#ffeb3b')
draw_box(ax, 3.5, 0.4, 3, 1, "LBAGuardrail\nBounded Tape & Config Hash", facecolor='#4caf50')
draw_box(ax, 7.5, 0.4, 2, 1, "Middleware\nExecution Loop", facecolor='#2196f3')

# Draw arrows
ax.annotate("", xy=(3.5, 0.9), xytext=(2.5, 0.9), arrowprops=dict(arrowstyle="->", lw=2))
ax.text(3, 1.0, "[state, observation]", ha='center', fontsize=10)

ax.annotate("", xy=(7.5, 0.9), xytext=(6.5, 0.9), arrowprops=dict(arrowstyle="->", lw=2))
ax.text(7, 1.0, "Continue or HALT", ha='center', fontsize=10)

ax.annotate("", xy=(1, 0.4), xytext=(8.5, 0.4), arrowprops=dict(arrowstyle="->", lw=2, connectionstyle="bar,fraction=-0.2"))
ax.text(4.75, 0.1, "Middleware calls Agent next step (if Continue)", ha='center', fontsize=10)

plt.title("LBA Guardrail Architecture Diagram", fontsize=16)
plt.tight_layout()

# Save the figure
output_dir = Path(__file__).resolve().parents[1] / "report_assets"
output_dir.mkdir(exist_ok=True)
plt.savefig(output_dir / "architecture_diagram.png", dpi=300)
print(f"Saved architecture diagram to {output_dir / 'architecture_diagram.png'}")
