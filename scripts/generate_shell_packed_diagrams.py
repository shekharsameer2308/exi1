"""
generate_shell_packed_diagrams.py
=================================
Generates clean, publication-grade, to-scale 2D cross section for the 4-tube
shell-packed catalytic membrane reactor.
Dimensions:
  Shell ID = 20.0 mm (R_shell = 10.0 mm)
  4 Membrane tubes: dt = 5.0 mm (rt = 2.5 mm, comparatively half radius of 10 mm tube)
  Pitch radius: R_pitch = 5.0 mm (R_shell / 2, equidistant from center)
  100% of shell volume around tubes is packed with catalyst.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Geometry definitions (all in mm)
D_shell = 20.0  # Shell inner diameter
R_shell = D_shell / 2.0  # 10.0 mm
dt = 5.0  # Membrane tube outer diameter
rt = dt / 2.0  # 2.5 mm
R_pitch = R_shell / 2.0  # 5.0 mm

# Tube center coordinates (90 degrees apart: right, top, left, bottom)
angles = [0.0, np.pi / 2.0, np.pi, 3.0 * np.pi / 2.0]
tube_centers = [(R_pitch * np.cos(a), R_pitch * np.sin(a)) for a in angles]

# Setup figure with wide layout to avoid any label clipping
fig, ax = plt.subplots(figsize=(9, 9), dpi=300)
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
pass_names = ["Pass 1", "Pass 2", "Pass 3", "Pass 4"]
for i, (cx, cy) in enumerate(tube_centers):
    # Outer membrane layer (Zeolite layer)
    membrane_outer = plt.Circle(
        (cx, cy), rt, facecolor="#2563eb", edgecolor="#1d4ed8", alpha=0.85, zorder=4,
        label="NaA Zeolite Membrane Layer" if i == 0 else ""
    )
    ax.add_patch(membrane_outer)

    # Ceramic support wall
    support_wall = plt.Circle(
        (cx, cy), rt - 0.1, facecolor="#93c5fd", edgecolor="none", zorder=5,
        label="Porous α-Al2O3 Support" if i == 0 else ""
    )
    ax.add_patch(support_wall)

    # Tube lumen (Permeate Sweep Channel)
    lumen = plt.Circle(
        (cx, cy), rt - tube_wall_thick, facecolor="#f8fafc", edgecolor="#1e40af", linewidth=1.2, zorder=6,
        label="Permeate Sweep Lumen (N2 sweep)" if i == 0 else ""
    )
    ax.add_patch(lumen)

    # Pass label cleanly centered in white lumen
    ax.text(cx, cy, f"P{i+1}", ha="center", va="center", fontsize=10, fontweight="bold", color="#1e3a8a", zorder=7)

# 4. Center Axis Crosshair and Pitch Circle
pitch_circle = plt.Circle((0, 0), R_pitch, fill=False, edgecolor="#64748b", linestyle="--", linewidth=1.2, zorder=3)
ax.add_patch(pitch_circle)
ax.plot([0], [0], "+", color="#0f172a", markersize=10, mew=1.5, zorder=8)

# 5. Dimension Annotations - positioned cleanly without overlaps
# A. Shell diameter D = 20 mm (along 45-degree angle or horizontal below)
# Show diameter arrow horizontally across lower third
y_diam = -11.0
ax.annotate(
    "", xy=(-R_shell, y_diam), xytext=(R_shell, y_diam),
    arrowprops=dict(arrowstyle="<->", color="#0f172a", lw=1.4), zorder=9
)
ax.plot([-R_shell, -R_shell], [-R_shell, y_diam], color="#94a3b8", linestyle=":", lw=1.0, zorder=3)
ax.plot([R_shell, R_shell], [-R_shell, y_diam], color="#94a3b8", linestyle=":", lw=1.0, zorder=3)
ax.text(0, y_diam - 0.5, "Shell ID = 20.0 mm", ha="center", va="top", fontsize=9, fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#94a3b8", alpha=0.95), zorder=10)

# B. Pitch radius Rpitch = 5.0 mm (arrow from center pointing down-right at 315 deg to avoid tubes)
ang_pr = -np.pi / 4.0
px_pr = R_pitch * np.cos(ang_pr)
py_pr = R_pitch * np.sin(ang_pr)
ax.annotate(
    "", xy=(0, 0), xytext=(px_pr, py_pr),
    arrowprops=dict(arrowstyle="<-", color="#b91c1c", lw=1.4), zorder=9
)
ax.text(px_pr * 0.5 - 0.5, py_pr * 0.5 - 0.8, "R_pitch = 5.0 mm\n(R_shell / 2)",
        ha="right", va="top", fontsize=8, color="#b91c1c", fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#fca5a5", alpha=0.95), zorder=10)

# C. Tube OD = 5.0 mm (callout on Pass 2 at top)
tc_top = tube_centers[1]  # (0, 5.0)
ax.annotate(
    "Tube OD = 5.0 mm\n(rt = 2.5 mm, half radius)",
    xy=(tc_top[0] + rt, tc_top[1]),
    xytext=(6.5, 9.5),
    arrowprops=dict(arrowstyle="->", color="#1e40af", lw=1.2),
    fontsize=8, color="#1e40af", fontweight="bold",
    bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#93c5fd", alpha=0.95), zorder=10
)

# D. Wall gap = 2.5 mm (callout on Pass 1 at right)
ax.annotate(
    "Wall gap: 2.5 mm",
    xy=(tube_centers[0][0] + rt + 1.25, 0),
    xytext=(11.5, 3.5),
    arrowprops=dict(arrowstyle="->", color="#334155", lw=1.1),
    fontsize=8, fontweight="bold", color="#334155",
    bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#cbd5e1", alpha=0.95), zorder=10
)

# E. Tube-to-tube gap = 2.07 mm (callout between Pass 1 and Pass 2)
mid_x = (tube_centers[0][0] + tube_centers[1][0]) / 2.0
mid_y = (tube_centers[0][1] + tube_centers[1][1]) / 2.0
ax.annotate(
    "Inter-tube gap: 2.07 mm\n(Packed catalyst, gap/dp = 6.9)",
    xy=(mid_x, mid_y),
    xytext=(-9.5, 9.5),
    arrowprops=dict(arrowstyle="->", color="#047857", lw=1.1),
    fontsize=8, fontweight="bold", color="#047857",
    bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#a7f3d0", alpha=0.95), zorder=10
)

# F. Center catalyst core gap
ax.annotate(
    "Center gap: 2.5 mm\n(Packed catalyst)",
    xy=(0, 2.5 / 2.0),
    xytext=(-10.5, 3.0),
    arrowprops=dict(arrowstyle="->", color="#047857", lw=1.1),
    fontsize=8, fontweight="bold", color="#047857",
    bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#a7f3d0", alpha=0.95), zorder=10
)

ax.set_xlim(-16, 17)
ax.set_ylim(-16, 16)
ax.set_title("Four-Tube Shell-Packed Catalytic Membrane Reactor\n"
             "All Shell Volume Packed with Catalyst (75% Ac) | 4 Membrane Passes Equidistant at Half Radius",
             fontsize=11, fontweight="bold", pad=14)

ax.axis("off")
plt.legend(loc="lower center", bbox_to_anchor=(0.5, -0.12), ncol=2, fontsize=8, frameon=True)
plt.tight_layout()

out_path = "figures/dme_shell_packed_cross_section.png"
plt.savefig(out_path, dpi=300, bbox_inches="tight")
print(f"Saved: {out_path}")
