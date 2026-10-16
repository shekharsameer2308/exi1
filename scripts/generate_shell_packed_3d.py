"""
generate_shell_packed_3d.py
===========================
Generates a 3D isometric cutaway diagram of the 4-tube shell-packed catalytic
membrane reactor where the ENTIRE outer shell is packed with catalyst, and 4
membrane tubes of half-radius (dt = 5.0 mm, rt = 2.5 mm) run along the reactor
length equidistant from the center at R_pitch = R_shell / 2 = 5.0 mm.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Geometry parameters (in mm)
D_shell = 20.0
R_shell = D_shell / 2.0  # 10.0 mm
dt = 5.0
rt = dt / 2.0  # 2.5 mm
R_pitch = R_shell / 2.0  # 5.0 mm
L_vis = 50.0  # Scaled length for visualization

# Tube centers (equidistant from center at 90 deg)
angles = [0.0, np.pi / 2.0, np.pi, 3.0 * np.pi / 2.0]
centers = [(R_pitch * np.cos(a), R_pitch * np.sin(a)) for a in angles]

fig = plt.figure(figsize=(10, 8), dpi=300)
ax = fig.add_subplot(111, projection='3d')

# Mesh definitions
z_grid = np.linspace(0, L_vis, 40)
theta_full = np.linspace(0, 2 * np.pi, 36)
# 90-degree quadrant cutaway: show 3/4 cylinder (pi/2 to 2*pi)
theta_cut = np.linspace(np.pi / 2, 2 * np.pi, 45)

Z_mesh_cut, Theta_cut = np.meshgrid(z_grid, theta_cut)
Z_mesh_full, Theta_full = np.meshgrid(z_grid, theta_full)

# 1. Outer Steel Shell (translucent silver with cutaway)
X_shell = (R_shell + 1.5) * np.cos(Theta_cut)
Y_shell = (R_shell + 1.5) * np.sin(Theta_cut)
ax.plot_surface(X_shell, Y_shell, Z_mesh_cut, color='#94a3b8', alpha=0.20, edgecolor='none')

# 2. Catalyst Bed Volume (Entire Shell Interior, Emerald Green, 3/4 cutaway)
X_bed = R_shell * np.cos(Theta_cut)
Y_bed = R_shell * np.sin(Theta_cut)
ax.plot_surface(X_bed, Y_bed, Z_mesh_cut, color='#10b981', alpha=0.30, edgecolor='none')

# Cutaway edge planes (z from 0 to L_vis)
# Plane at angle = pi/2 (X=0, Y from 0 to R_shell)
Y_plane = np.linspace(0, R_shell, 15)
Z_p, Y_p = np.meshgrid(z_grid, Y_plane)
X_p = np.zeros_like(Y_p)
ax.plot_surface(X_p, Y_p, Z_p, color='#059669', alpha=0.45, edgecolor='none')

# Plane at angle = 2*pi (Y=0, X from 0 to R_shell)
X_plane = np.linspace(0, R_shell, 15)
Z_p2, X_p2 = np.meshgrid(z_grid, X_plane)
Y_p2 = np.zeros_like(X_p2)
ax.plot_surface(X_p2, Y_p2, Z_p2, color='#059669', alpha=0.45, edgecolor='none')

# 3. Four Membrane Tubes (Royal Blue cylinders running full length)
for i, (cx, cy) in enumerate(centers):
    # Tube outer membrane surface
    X_tube = cx + rt * np.cos(Theta_full)
    Y_tube = cy + rt * np.sin(Theta_full)
    ax.plot_surface(X_tube, Y_tube, Z_mesh_full, color='#2563eb', alpha=0.85, edgecolor='none')

    # Draw end cap rings
    z_end = L_vis
    xc_end = cx + (rt - 0.7) * np.cos(theta_full)
    yc_end = cy + (rt - 0.7) * np.sin(theta_full)
    ax.plot(xc_end, yc_end, [z_end] * len(theta_full), color='#1e3a8a', lw=1.5)

    # Permeate exit flow vector (arrow pointing out of each tube lumen at z=L)
    ax.quiver(cx, cy, L_vis, 0, 0, 10, color='#1d4ed8', lw=2.2, arrow_length_ratio=0.3)

# Retentate exit flow from catalyst bed
ax.quiver(0, 0, L_vis, 0, 0, 8, color='#047857', lw=2.5, arrow_length_ratio=0.3)

# Inlet feed arrows at z=0 (entering shell packed catalyst bed)
ax.quiver(0, -6, -10, 0, 0, 8, color='#059669', lw=2.5, arrow_length_ratio=0.35)
ax.quiver(0, 0, -10, 0, 0, 8, color='#059669', lw=2.5, arrow_length_ratio=0.35)

# Sweep inlet arrows at z=0 (entering 4 tube lumens)
for cx, cy in centers:
    ax.quiver(cx, cy, -10, 0, 0, 8, color='#3b82f6', lw=1.8, arrow_length_ratio=0.35)

# Annotations
ax.text(0, -12, -12, "Feed Syngas: CO2 + 3H2\n(40 bar, 250 °C -> Shell Bed)", color='#047857', fontsize=8, fontweight='bold')
ax.text(-12, 0, -12, "Sweep N2 -> 4 Tube Lumens\n(1 bar, 4 Tube Passes)", color='#1d4ed8', fontsize=8, fontweight='bold')
ax.text(0, 0, L_vis + 12, "Retentate Exit: DME + CO + unreacted syngas", color='#047857', fontsize=8, fontweight='bold')
ax.text(centers[0][0], centers[0][1], L_vis + 12, "Permeate Exit:\nH2O vapor + N2", color='#1d4ed8', fontsize=8, fontweight='bold')

ax.set_box_aspect([1, 1, 2.0])
ax.view_init(elev=22, azim=-55)
ax.set_axis_off()

plt.title("Four-Tube Shell-Packed Catalytic Membrane Reactor (3D Cutaway)\n"
          "Outer Shell ID = 20 mm Packed with Catalyst | 4 Membrane Tubes (dt = 5 mm) at Rpitch = 5 mm",
          fontsize=10, fontweight='bold', pad=15)
plt.tight_layout()

out_path = "figures/dme_shell_packed_3d_cutaway.png"
plt.savefig(out_path, dpi=300, bbox_inches="tight")
print(f"Saved: {out_path}")
