"""
generate_shell_packed_diagrams.py
=================================
Generates to-scale 2D cross section and 3D schematic for the 4-tube shell-packed
membrane reactor where the ENTIRE outer shell is packed with catalyst, and 4
membrane tubes of half-radius (dt = 5.0 mm, rt = 2.5 mm) are positioned equidistant
from the center at pitch radius R_pitch = R_shell / 2 = 5.0 mm.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Geometry definitions (all in mm)
D_shell = 20.0  # Shell inner diameter
R_shell = D_shell / 2.0  # 10.0 mm
dt = 5.0  # Membrane tube outer diameter (half radius of 10 mm tube)
rt = dt / 2.0  # 2.5 mm
R_pitch = R_shell / 2.0  # 5.0 mm (equidistant from center at half shell radius)

# Tube center coordinates (90 degrees apart)
angles = [0.0, np.pi / 2.0, np.pi, 3.0 * np.pi / 2.0]
tube_centers = [(R_pitch * np.cos(a), R_pitch * np.sin(a)) for a in angles]

# Setup figure
fig, ax = plt.subplots(figsize=(8, 8), dpi=300)
ax.set_aspect("equal")

# 1. Outer Shell Wall (Steel)
shell_wall_thick = 2.5
shell_outer_circle = plt.Circle(
    (0, 0), R_shell + shell_wall_thick, color="#94a3b8", zorder=1, label="SS 316L Shell Wall (2.5 mm thick)"
)
ax.add_patch(shell_outer_circle)

# 2. Entire Shell Interior: Packed Catalyst Bed (Emerald Green)
catalyst_bed = plt.Circle(
    (0, 0), R_shell, color="#10b981", alpha=0.35, zorder=2, label="Packed Catalyst Bed (Cu/ZnO + HZSM-5, 75% Ac)"
)
ax.add_patch(catalyst_bed)

# Shell inner wall border
shell_inner_border = plt.Circle((0, 0), R_shell, fill=False, edgecolor="#334155", linewidth=2.0, zorder=3)
ax.add_patch(shell_inner_border)

# Add catalyst pellet stippling pattern inside catalyst bed
np.random.seed(42)
n_pellets = 600
r_pts = np.sqrt(np.random.uniform(0, R_shell ** 2, n_pellets * 2))
theta_pts = np.random.uniform(0, 2 * np.pi, n_pellets * 2)
x_pts = r_pts * np.cos(theta_pts)
y_pts = r_pts * np.sin(theta_pts)

# Filter out points inside the 4 membrane tubes
valid_x, valid_y = [], []
for x, y in zip(x_pts, y_pts):
    inside_tube = False
    for cx, cy in tube_centers:
        if (x - cx) ** 2 + (y - cy) ** 2 <= (rt * 1.05) ** 2:
            inside_tube = True
            break
    if not inside_tube and (x ** 2 + y ** 2 <= (R_shell - 0.2) ** 2):
        valid_x.append(x)
        valid_y.append(y)
    if len(valid_x) >= 350:
        break

ax.scatter(valid_x, valid_y, s=6, color="#047857", alpha=0.5, zorder=3, edgecolors="none")

# 3. Four Membrane Tubes (4 Tube Passes)
tube_wall_thick = 0.8  # Porous ceramic support thickness
for i, (cx, cy) in enumerate(tube_centers):
    # Outer membrane layer (Zeolite layer)
    membrane_outer = plt.Circle(
        (cx, cy), rt, color="#2563eb", alpha=0.85, zorder=4,
        label="NaA Zeolite Membrane Layer" if i == 0 else ""
    )
    ax.add_patch(membrane_outer)

    # Ceramic support wall
    support_wall = plt.Circle(
        (cx, cy), rt - 0.1, color="#93c5fd", zorder=5,
        label="Porous α-Al2O3 Support" if i == 0 else ""
    )
    ax.add_patch(support_wall)

    # Tube lumen (Permeate Sweep Channel)
    lumen = plt.Circle(
        (cx, cy), rt - tube_wall_thick, color="#f8fafc", edgecolor="#1e40af", linewidth=1.2, zorder=6,
        label="Permeate Sweep Lumen (N2 sweep)" if i == 0 else ""
    )
    ax.add_patch(lumen)

    # Pass label
    ax.text(cx, cy, f"P{i+1}", ha="center", va="center", fontsize=9, fontweight="bold", color="#1e3a8a", zorder=7)

# 4. Center Axis Crosshair and Pitch Circle
pitch_circle = plt.Circle((0, 0), R_pitch, fill=False, edgecolor="#64748b", linestyle="--", linewidth=1.2, zorder=3)
ax.add_patch(pitch_circle)
ax.plot([0], [0], "+", color="#0f172a", markersize=10, mew=1.5, zorder=8)

# 5. Dimension Annotations
# Shell diameter D = 20 mm
ax.annotate(
    "", xy=(-R_shell, 0), xytext=(R_shell, 0),
    arrowprops=dict(arrowstyle="<->", color="#0f172a", lw=1.4), zorder=9
)
ax.text(0, -1.2, "Shell ID = 20.0 mm", ha="center", va="top", fontsize=9, fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#94a3b8", alpha=0.9), zorder=10)

# Pitch radius Rpitch = 5.0 mm
ax.annotate(
    "", xy=(0, 0), xytext=(tube_centers[0][0], tube_centers[0][1]),
    arrowprops=dict(arrowstyle="->", color="#b91c1c", lw=1.4), zorder=9
)
ax.text(2.5, 0.8, "R_pitch = 5.0 mm\n(R_shell / 2)", ha="center", va="bottom", fontsize=8, color="#b91c1c", fontweight="bold", zorder=10)

# Membrane tube diameter dt = 5.0 mm
tc_top = tube_centers[1]
ax.annotate(
    "", xy=(tc_top[0] - rt, tc_top[1]), xytext=(tc_top[0] + rt, tc_top[1]),
    arrowprops=dict(arrowstyle="<->", color="#1e40af", lw=1.2), zorder=9
)
ax.text(tc_top[0], tc_top[1] + 3.2, "Tube OD = 5.0 mm\n(rt = 2.5 mm, half radius)", ha="center", va="bottom", fontsize=8, color="#1e40af", fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#93c5fd", alpha=0.9), zorder=10)

# Gap annotations
# Gap to shell wall = 2.5 mm
ax.annotate(
    "Wall gap: 2.5 mm", xy=(tube_centers[0][0] + rt, 0), xytext=(11.5, 3.5),
    arrowprops=dict(arrowstyle="->", color="#334155", lw=1.0),
    fontsize=8, fontweight="bold", color="#334155",
    bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#cbd5e1", alpha=0.9)
)

# Gap to adjacent tube = 2.07 mm
mid_x = (tube_centers[0][0] + tube_centers[1][0]) / 2.0
mid_y = (tube_centers[0][1] + tube_centers[1][1]) / 2.0
ax.annotate(
    "Tube gap: 2.07 mm\n(Packed catalyst)", xy=(mid_x, mid_y), xytext=(7.5, 7.5),
    arrowprops=dict(arrowstyle="->", color="#047857", lw=1.0),
    fontsize=8, fontweight="bold", color="#047857",
    bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#a7f3d0", alpha=0.9)
)

ax.set_xlim(-14, 15)
ax.set_ylim(-14, 15)
ax.set_title("Four-Tube Shell-Packed Membrane Reactor\n(All Shell Space Packed with Catalyst; 4 Tube Passes Equidistant at Half Radius)",
             fontsize=11, fontweight="bold", pad=12)

ax.axis("off")
plt.legend(loc="lower center", bbox_to_anchor=(0.5, -0.16), ncol=2, fontsize=8, frameon=True)
plt.tight_layout()

out_path = "figures/dme_shell_packed_cross_section.png"
plt.savefig(out_path, dpi=300, bbox_inches="tight")
print(f"Saved: {out_path}")
