"""
generate_dme_3d.py
==================
Generates a 3D isometric cutaway architectural diagram of the 4-tube
sleeve bundle catalytic membrane reactor for direct CO2-to-DME synthesis.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# Reactor Geometry Parameters (Worked Check & Recommended Design)
d_mm = 6.0       # Membrane outer diameter
t_mm = 1.12      # Catalyst sleeve thickness
ds_mm = d_mm + 2 * t_mm  # 8.24 mm
D_mm = (1.0 + np.sqrt(2.0)) * ds_mm  # 19.88 mm
L_mm = 60.0      # Scaled visualization length for 3D aspect ratio

fig = plt.figure(figsize=(10, 8), dpi=300)
ax = fig.add_subplot(111, projection='3d')

# Tube Center Offsets
offset = ds_mm / 2.0
centers = [
    (offset, offset),
    (-offset, offset),
    (-offset, -offset),
    (offset, -offset)
]

# Generate Cylinder Mesh Data
z_grid = np.linspace(0, L_mm, 40)
theta_full = np.linspace(0, 2 * np.pi, 36)
# For cutaway shell: 3/4 cylinder (angles from pi/2 to 2*pi)
theta_cutaway = np.linspace(np.pi / 2, 2 * np.pi, 45)

Z_mesh_cut, Theta_cut = np.meshgrid(z_grid, theta_cutaway)
Z_mesh_full, Theta_full = np.meshgrid(z_grid, theta_full)

# 1. Shell Outer Wall (Translucent Silver / Slate with 90-degree cutaway)
R_shell = D_mm / 2.0
X_shell = R_shell * np.cos(Theta_cut)
Y_shell = R_shell * np.sin(Theta_cut)
ax.plot_surface(X_shell, Y_shell, Z_mesh_cut, color='#cbd5e1', alpha=0.25, edgecolor='none')

# Cutaway edge lines
ax.plot([0, R_shell * np.cos(np.pi/2)], [0, R_shell * np.sin(np.pi/2)], [0, 0], color='#475569', lw=1.5)
ax.plot([0, R_shell * np.cos(2*np.pi)], [0, R_shell * np.sin(2*np.pi)], [0, 0], color='#475569', lw=1.5)
ax.plot([0, R_shell * np.cos(np.pi/2)], [0, R_shell * np.sin(np.pi/2)], [L_mm, L_mm], color='#475569', lw=1.5)
ax.plot([0, R_shell * np.cos(2*np.pi)], [0, R_shell * np.sin(2*np.pi)], [L_mm, L_mm], color='#475569', lw=1.5)

# 2. Four Catalyst Sleeves (Emerald Green)
R_sleeve = ds_mm / 2.0
R_mem = d_mm / 2.0

for i, (cx, cy) in enumerate(centers):
    # Catalyst sleeve outer surface
    Xs = cx + R_sleeve * np.cos(Theta_full)
    Ys = cy + R_sleeve * np.sin(Theta_full)
    ax.plot_surface(Xs, Ys, Z_mesh_full, color='#10b981', alpha=0.55, edgecolor='none')

    # Membrane tube outer surface (Blue)
    Xm = cx + R_mem * np.cos(Theta_full)
    Ym = cy + R_mem * np.sin(Theta_full)
    ax.plot_surface(Xm, Ym, Z_mesh_full, color='#3b82f6', alpha=0.9, edgecolor='none')

    # Annulus cap rings at z = 0 (Inlet)
    ax.plot(cx + R_sleeve * np.cos(theta_full), cy + R_sleeve * np.sin(theta_full), 0, color='#047857', lw=1.2)
    ax.plot(cx + R_mem * np.cos(theta_full), cy + R_mem * np.sin(theta_full), 0, color='#1d4ed8', lw=1.2)

    # Annulus cap rings at z = L (Outlet)
    ax.plot(cx + R_sleeve * np.cos(theta_full), cy + R_sleeve * np.sin(theta_full), L_mm, color='#047857', lw=1.2)
    ax.plot(cx + R_mem * np.cos(theta_full), cy + R_mem * np.sin(theta_full), L_mm, color='#1d4ed8', lw=1.2)

# 3. Flow Direction Callout Arrows
# Feed syngas into catalyst sleeves
ax.quiver(offset, offset, -15, 0, 0, 12, color='#047857', lw=2.2, arrow_length_ratio=0.35)
ax.text(offset, offset, -18, "Feed Syngas In\n(CO2 + 3 H2)", color='#047857', fontsize=8, fontweight='bold', ha='center')

# Permeate extraction out of lumens
ax.quiver(-offset, -offset, -15, 0, 0, 12, color='#1d4ed8', lw=2.2, arrow_length_ratio=0.35)
ax.text(-offset, -offset, -18, "Permeate In / Sweep\n(N2 Sweep)", color='#1d4ed8', fontsize=8, fontweight='bold', ha='center')

# Retentate product stream out
ax.quiver(offset, offset, L_mm + 2, 0, 0, 14, color='#047857', lw=2.2, arrow_length_ratio=0.35)
ax.text(offset, offset, L_mm + 18, "Retentate Out\n(DME + CO + Unreacted)", color='#047857', fontsize=8, fontweight='bold', ha='center')

# Water permeate out
ax.quiver(-offset, -offset, L_mm + 2, 0, 0, 14, color='#1d4ed8', lw=2.2, arrow_length_ratio=0.35)
ax.text(-offset, -offset, L_mm + 18, "Permeate Out\n(H2O Vapor)", color='#1d4ed8', fontsize=8, fontweight='bold', ha='center')

# 4. View Angle and Lighting Setup
ax.view_init(elev=26, azim=-55)
ax.set_box_aspect([1.0, 1.0, 1.8])

# Labels and Annotations
ax.set_xlabel('X [mm]', fontsize=9, labelpad=5)
ax.set_ylabel('Y [mm]', fontsize=9, labelpad=5)
ax.set_zlabel('Axial Bed Length Z [mm]', fontsize=9, labelpad=5)

ax.set_xlim(-R_shell * 1.3, R_shell * 1.3)
ax.set_ylim(-R_shell * 1.3, R_shell * 1.3)
ax.set_zlim(-20, L_mm + 25)

plt.title("3D Cutaway Architecture: Four-Tube Sleeve Bundle CMR\n"
          f"(Shell D = {D_mm:.1f} mm, Tube d = {d_mm:.1f} mm, Sleeve t = {t_mm:.2f} mm)",
          fontsize=11, fontweight='bold', pad=12)

# Custom legend proxies
import matplotlib.lines as mlines
p_shell = mlines.Line2D([], [], color='#94a3b8', lw=4, label='Outer Cylindrical Shell')
p_sleeve = mlines.Line2D([], [], color='#10b981', lw=4, label='Catalyst Annular Sleeve (Cu/ZnO/Al2O3 + Acid)')
p_mem = mlines.Line2D([], [], color='#3b82f6', lw=4, label='Inorganic Membrane Tube (NaA/LTA Zeolite)')
p_void = mlines.Line2D([], [], color='#64748b', linestyle='--', lw=2, label='Sealed Voids / Inert Core')

ax.legend(handles=[p_shell, p_sleeve, p_mem, p_void], loc='upper right', bbox_to_anchor=(1.15, 0.95), fontsize=8)

plt.tight_layout()
plt.savefig('figures/dme_bundle_3d_cutaway.png', dpi=300)
plt.close()
print(">> Successfully generated: figures/dme_bundle_3d_cutaway.png")
