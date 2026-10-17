"""
generate_dme_cfd_3d.py
======================
3D Transport-Kinetic Flow Field Visualization for the Four-Tube Shell-Packed
Catalytic Membrane Reactor (Case Study B).

All physical data are extracted from the 1D stiff-BVP ODE solver (BDF method).
The visualisation maps real axial concentration gradients, transmembrane water
flux vectors, and superficial velocity decay onto a 3D reactor geometry using
matplotlib / NumPy.

Outputs
-------
  figures/dme_cfd_3d_flow.png       -- 3D annotated flow-field rendering
  figures/dme_cfd_axial_profiles.png -- 4-panel axial profiles (MR vs TR)
"""

import sys
import os

# Make project root importable regardless of CWD
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import warnings
warnings.filterwarnings("ignore")

from dme_membrane_reactor import run_dme_simulation
from dme_bundle_reactor import bundle_layout

# ---------------------------------------------------------------------------
# Palette (muted: slate, emerald, red, gray — per AGENTS.md)
# ---------------------------------------------------------------------------
C_SLATE   = "#475569"
C_EMERALD = "#10b981"
C_RED     = "#ef4444"
C_GRAY    = "#6b7280"
C_GOLD    = "#b45309"
C_BLUE    = "#2563eb"
C_SKY     = "#0ea5e9"

FIGURES_DIR = os.path.join(_ROOT, "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Reactor Geometry — Case Study B: Four-Tube Shell-Packed (d_t = 5 mm)
# ---------------------------------------------------------------------------
D_SHELL_M = 0.020          # shell inner diameter [m]
D_TUBE_M  = 0.005          # membrane tube outer diameter [m]
R_PITCH_M = 0.005          # tube centre offset from shell axis [m]
L_M       = 1.0            # reactor length [m]

# Tube centre positions (symmetric quadrant arrangement)
TUBE_CENTRES = np.array([
    [ R_PITCH_M,  0.0],
    [-R_PITCH_M,  0.0],
    [ 0.0,  R_PITCH_M],
    [ 0.0, -R_PITCH_M],
])

# ---------------------------------------------------------------------------
# Run 1D ODE — Membrane Reactor (MR) and Traditional Reactor (TR)
# ---------------------------------------------------------------------------
print("Running 1D ODE solver — Membrane Reactor (NaA, T=250 C, P=40 bar)...")
layout = bundle_layout(catalyst="shell_packed", d=D_TUBE_M)

res_mr = run_dme_simulation(
    layout,
    membrane_type="NaA",
    is_membrane=True,
    T_C=250.0,
    P_ret_bar=40.0,
    L_m=L_M,
)

print("Running 1D ODE solver — Traditional Packed-Bed Reactor (TR)...")
res_tr = run_dme_simulation(
    layout,
    membrane_type="NaA",
    is_membrane=False,
    T_C=250.0,
    P_ret_bar=40.0,
    L_m=L_M,
)

assert res_mr["success"], "MR ODE solver failed — cannot proceed."
assert res_tr["success"], "TR ODE solver failed — cannot proceed."

# Axial coordinate and molar flow profiles [mol/s] for 6 species
z      = np.array(res_mr["z"])           # length Nz
F_mr   = np.array(res_mr["profiles_ret"])   # shape (6, Nz)
F_tr   = np.array(res_tr["profiles_ret"])
F_perm = np.array(res_mr["profiles_perm"])

Nz = len(z)
SPECIES = ["CO2", "H2", "H2O", "CH3OH", "CO", "DME"]
IDX = {s: i for i, s in enumerate(SPECIES)}

F_tot_mr = F_mr.sum(axis=0)          # total molar flow [mol/s] axial
F_tot_tr = F_tr.sum(axis=0)
F_CO2_in = F_mr[IDX["CO2"], 0]

# Derived axial fields
X_CO2_mr  = (F_CO2_in - F_mr[IDX["CO2"], :]) / F_CO2_in * 100.0
X_CO2_tr  = (F_CO2_in - F_tr[IDX["CO2"], :]) / F_CO2_in * 100.0
Y_DME_mr  = 2.0 * F_mr[IDX["DME"], :] / F_CO2_in * 100.0
Y_DME_tr  = 2.0 * F_tr[IDX["DME"], :] / F_CO2_in * 100.0

# Water removal flux along reactor [mol/(m·s)] per unit length (sum of 4 tubes)
Pm = layout["Pm"]  # membrane perimeter per unit length [m/m] = m_perimeter
F_H2O_perm_axial = np.gradient(F_perm[IDX["H2O"], :], z)   # mol/s per m
# Transmembrane flux magnitude per m^2 (using Pm as tube perimeter/m)
flux_H2O = np.maximum(F_H2O_perm_axial / (Pm + 1e-20), 0.0)  # mol/(m^2·s)

# Superficial velocity proxy: proportional to total molar flow
# (isothermal isobaric → u_s ∝ F_tot)
u_s_rel = F_tot_mr / F_tot_mr[0]   # normalised to inlet

print(f"\n  MR:  X_CO2 = {res_mr['X_CO2']:.2f}%  |  Y_DME = {res_mr['Y_DME']:.2f}%")
print(f"  TR:  X_CO2 = {res_tr['X_CO2']:.2f}%  |  Y_DME = {res_tr['Y_DME']:.2f}%")


# ===========================================================================
# Figure 1 — 3D Transport-Kinetic Flow Field
# ===========================================================================
def make_cylinder(xc, yc, r, z0, z1, Nz=30, Nphi=40):
    """Return x,y,z surface arrays for a cylinder of radius r at (xc,yc)."""
    phi = np.linspace(0, 2 * np.pi, Nphi)
    zz  = np.linspace(z0, z1, Nz)
    PHI, ZZ = np.meshgrid(phi, zz)
    XX = xc + r * np.cos(PHI)
    YY = yc + r * np.sin(PHI)
    return XX, YY, ZZ


def make_shell_surface(r, z0, z1, Nz=30, Nphi=60):
    """Outer shell (tube) surface arrays."""
    phi = np.linspace(0, 2 * np.pi, Nphi)
    zz  = np.linspace(z0, z1, Nz)
    PHI, ZZ = np.meshgrid(phi, zz)
    XX = r * np.cos(PHI)
    YY = r * np.sin(PHI)
    return XX, YY, ZZ


print("\nGenerating 3D flow-field figure...")

fig = plt.figure(figsize=(14, 9))
ax  = fig.add_subplot(111, projection="3d")

R_shell = D_SHELL_M / 2   # 0.010 m
R_tube  = D_TUBE_M  / 2   # 0.0025 m

# ---- Shell outer surface (transparent) ----
Xs, Ys, Zs = make_shell_surface(R_shell, 0, L_M, Nz=2, Nphi=60)
ax.plot_surface(Xs * 1e3, Ys * 1e3, Zs * 1e3,
                alpha=0.07, color=C_GRAY, linewidth=0, zorder=1)

# ---- Colour the shell surface by local CO2 conversion ----
# Map conversion along Z axis → colour of outer shell
cmap_conv = plt.get_cmap("RdYlGn")
norm_conv  = mcolors.Normalize(vmin=0, vmax=100)

Nphi_sh = 60
phi_sh  = np.linspace(0, 2 * np.pi, Nphi_sh)
for iz in range(Nz - 1):
    z0_mm = z[iz]   * 1e3
    z1_mm = z[iz+1] * 1e3
    conv  = X_CO2_mr[iz]
    rgba  = cmap_conv(norm_conv(conv))
    verts = []
    for ip in range(Nphi_sh - 1):
        xs = [
            R_shell*1e3*np.cos(phi_sh[ip]),
            R_shell*1e3*np.cos(phi_sh[ip+1]),
            R_shell*1e3*np.cos(phi_sh[ip+1]),
            R_shell*1e3*np.cos(phi_sh[ip]),
        ]
        ys = [
            R_shell*1e3*np.sin(phi_sh[ip]),
            R_shell*1e3*np.sin(phi_sh[ip+1]),
            R_shell*1e3*np.sin(phi_sh[ip+1]),
            R_shell*1e3*np.sin(phi_sh[ip]),
        ]
        zs = [z0_mm, z0_mm, z1_mm, z1_mm]
        verts.append(list(zip(xs, ys, zs)))
    poly = Poly3DCollection(verts, alpha=0.22, linewidth=0)
    poly.set_facecolor(rgba)
    ax.add_collection3d(poly)

# ---- Membrane tubes (solid blue) ----
for (xc, yc) in TUBE_CENTRES:
    Xt, Yt, Zt = make_cylinder(xc*1e3, yc*1e3, R_tube*1e3, 0, L_M*1e3,
                                Nz=30, Nphi=30)
    ax.plot_surface(Xt, Yt, Zt, alpha=0.75, color=C_BLUE,
                    linewidth=0, zorder=5)

# ---- Catalyst bed fill — semi-transparent emerald ----
# Approximate catalyst zone as shell minus 4 tubes at a few cross-sections
phi_fill = np.linspace(0, 2*np.pi, 120)
for iz_frac in np.linspace(0, 1, 8):
    zval_mm = iz_frac * L_M * 1e3
    xring = R_shell * 0.70 * 1e3 * np.cos(phi_fill)
    yring = R_shell * 0.70 * 1e3 * np.sin(phi_fill)
    ax.plot(xring, yring, zval_mm * np.ones_like(xring),
            color=C_EMERALD, alpha=0.08, linewidth=0.5)

# ---- Axial flow streamlines (arrows along z at radial positions) ----
# Sample 12 streamline starting positions in the catalyst annular region
N_stream = 12
psi_stream = np.linspace(0, 2*np.pi, N_stream, endpoint=False)
r_stream   = R_shell * 0.72  # radial position in catalyst bed

# Arrow step size in z [mm]
z_arrow_positions = np.linspace(0, L_M*1e3, 15)

for psi in psi_stream:
    xs_c = r_stream * 1e3 * np.cos(psi)
    ys_c = r_stream * 1e3 * np.sin(psi)

    # Skip if inside a tube
    inside = False
    for (xc, yc) in TUBE_CENTRES:
        if np.hypot(xs_c - xc*1e3, ys_c - yc*1e3) < R_tube*1e3 * 1.2:
            inside = True
            break
    if inside:
        continue

    for zi_mm in z_arrow_positions[:-1]:
        iz = np.searchsorted(z * 1e3, zi_mm)
        iz = min(iz, Nz - 2)
        u_frac = float(u_s_rel[iz])
        color  = cmap_conv(norm_conv(float(X_CO2_mr[iz])))
        arrow_len = 30.0 * u_frac     # scale arrow length by velocity
        ax.quiver(xs_c, ys_c, zi_mm,
                  0, 0, arrow_len,
                  color=color, alpha=0.65, linewidth=0.8,
                  arrow_length_ratio=0.35,
                  normalize=False)

# ---- Transmembrane water-flux vectors (radial inward toward tubes) ----
# Show at 6 axial positions
z_flux_positions = np.linspace(0.05, 0.95, 8) * L_M * 1e3
for zi_mm in z_flux_positions:
    iz = np.searchsorted(z * 1e3, zi_mm)
    iz = min(iz, Nz - 1)
    flux_norm = float(flux_H2O[iz]) / (float(flux_H2O.max()) + 1e-20)
    if flux_norm < 0.01:
        continue
    arrow_r = 3.0 * flux_norm   # [mm] arrow length scaled to flux

    for (xc, yc) in TUBE_CENTRES:
        # Arrow from outer edge of tube to tube surface
        x_start = xc*1e3 + (R_tube*1e3 + arrow_r * 2.0) * np.sign(xc) if abs(xc) > 0 \
                  else (R_tube*1e3 + arrow_r * 2.0) * np.sign(yc + 1e-20) * 0.0
        # Simplified: point from just outside tube toward tube centre
        dx_hat = -np.sign(xc + yc * 1e-9) if abs(xc) > 0 else 0.0
        dy_hat = -np.sign(yc + xc * 1e-9) if abs(yc) > 0 else 0.0
        x_s = xc*1e3 + (R_tube*1e3 + arrow_r*1.8) * (-dx_hat if dx_hat != 0 else 1e-9)
        y_s = yc*1e3 + (R_tube*1e3 + arrow_r*1.8) * (-dy_hat if dy_hat != 0 else 1e-9)
        ax.quiver(x_s, y_s, zi_mm,
                  dx_hat * arrow_r, dy_hat * arrow_r, 0,
                  color=C_SKY, alpha=0.80, linewidth=0.7,
                  arrow_length_ratio=0.5, normalize=False)

# ---- Inlet/outlet end caps ----
circle_phi = np.linspace(0, 2*np.pi, 80)
for z_cap, label, z_text_off in [(0, "Feed\n(CO₂/H₂, 40 bar)", -80),
                                   (L_M*1e3, "Product\n(DME-rich)", 30)]:
    ax.plot(R_shell*1e3*np.cos(circle_phi), R_shell*1e3*np.sin(circle_phi),
            z_cap * np.ones(80), color=C_GRAY, linewidth=0.8, alpha=0.4)
    ax.text(0, -R_shell*1e3 - 2, z_cap + z_text_off, label,
            fontsize=7.5, color=C_SLATE, ha="center", va="top", style="italic")

# ---- Colourbar ----
sm = cm.ScalarMappable(cmap=cmap_conv, norm=norm_conv)
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax, shrink=0.55, pad=0.01, aspect=22)
cbar.set_label("Local CO₂ Conversion  [%]", fontsize=9, color=C_SLATE)
cbar.ax.tick_params(labelsize=8, colors=C_SLATE)

# ---- Legend proxies ----
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor=C_BLUE,    alpha=0.75, label="NaA Membrane Tube (×4)"),
    Patch(facecolor=C_EMERALD, alpha=0.55, label="Cu/ZnO/Al₂O₃ Catalyst Bed"),
    Line2D([0],[0], color=cmap_conv(0.95), linewidth=2,
           label="Axial flow (coloured by conversion)"),
    Line2D([0],[0], color=C_SKY, linewidth=2,
           label="H₂O transmembrane flux"),
]
ax.legend(handles=legend_elements, loc="upper left",
          fontsize=7.5, framealpha=0.7, edgecolor=C_GRAY,
          bbox_to_anchor=(0.0, 1.0))

# ---- Axes labels & formatting ----
ax.set_xlabel("x  [mm]", fontsize=9, color=C_SLATE, labelpad=4)
ax.set_ylabel("y  [mm]", fontsize=9, color=C_SLATE, labelpad=4)
ax.set_zlabel("z  [mm]  (axial)", fontsize=9, color=C_SLATE, labelpad=4)
ax.set_title(
    "Four-Tube Shell-Packed Catalytic Membrane Reactor\n"
    "3D Transport-Kinetic Flow Field  |  NaA Zeolite  |  T = 250 °C, P = 40 bar",
    fontsize=10, color=C_SLATE, pad=8,
)
ax.tick_params(labelsize=7.5, colors=C_SLATE)
ax.view_init(elev=22, azim=-55)

# Key result annotation
ax.text2D(
    0.70, 0.92,
    f"X$_{{CO_2}}$ = {res_mr['X_CO2']:.1f}%\n"
    f"Y$_{{DME}}$  = {res_mr['Y_DME']:.1f}%\n"
    f"H₂O removed = {res_mr['water_removed_pct']:.1f}%",
    transform=ax.transAxes,
    fontsize=8.5, color=C_SLATE,
    verticalalignment="top",
    bbox=dict(boxstyle="round,pad=0.35", facecolor="white",
              edgecolor=C_GRAY, alpha=0.88),
)

plt.tight_layout()
out_3d = os.path.join(FIGURES_DIR, "dme_cfd_3d_flow.png")
fig.savefig(out_3d, dpi=300, bbox_inches="tight", facecolor="white")
plt.close(fig)
print(f"  Saved: {out_3d}")


# ===========================================================================
# Figure 2 — 4-Panel Axial Profiles (MR vs TR)
# ===========================================================================
print("\nGenerating 4-panel axial profiles figure...")

z_mm = z * 1e3   # [mm]

fig2, axes = plt.subplots(2, 2, figsize=(11, 8), constrained_layout=True)
fig2.suptitle(
    "Axial Concentration Profiles  —  Shell-Packed CMR (MR) vs. Traditional PBR (TR)\n"
    "NaA Zeolite  |  T = 250 °C, P = 40 bar  |  H₂/CO₂ = 3  |  GHSV = 1000 h⁻¹",
    fontsize=10, color=C_SLATE, y=1.01,
)

def _fmt(ax_, ylabel, ylim=None):
    ax_.set_xlabel("Axial position  z  [mm]", fontsize=9, color=C_SLATE)
    ax_.set_ylabel(ylabel, fontsize=9, color=C_SLATE)
    ax_.tick_params(labelsize=8.5, colors=C_SLATE)
    ax_.spines["top"].set_visible(False)
    ax_.spines["right"].set_visible(False)
    ax_.spines["left"].set_color(C_GRAY)
    ax_.spines["bottom"].set_color(C_GRAY)
    ax_.legend(fontsize=8, framealpha=0.7, edgecolor=C_GRAY)
    ax_.grid(axis="y", color=C_GRAY, alpha=0.25, linewidth=0.6)
    if ylim:
        ax_.set_ylim(ylim)

# Panel A: CO2 Conversion
ax_a = axes[0, 0]
ax_a.plot(z_mm, X_CO2_mr, color=C_EMERALD, linewidth=2.0, label="MR (NaA)")
ax_a.plot(z_mm, X_CO2_tr, color=C_RED,     linewidth=2.0, linestyle="--", label="TR (no membrane)")
ax_a.axhline(48.71, color=C_SLATE, linewidth=1.0, linestyle=":", label="Gibbs ceiling (48.7%)")
ax_a.set_title("CO₂ Conversion", fontsize=9.5, color=C_SLATE)
_fmt(ax_a, "X$_{CO_2}$  [%]", ylim=[0, 105])
ax_a.text(z_mm[-1]*0.95, res_mr["X_CO2"] + 2,
          f"{res_mr['X_CO2']:.1f}%", fontsize=8, color=C_EMERALD, ha="right")
ax_a.text(z_mm[-1]*0.95, res_tr["X_CO2"] - 5,
          f"{res_tr['X_CO2']:.1f}%", fontsize=8, color=C_RED, ha="right")

# Panel B: DME Yield
ax_b = axes[0, 1]
ax_b.plot(z_mm, Y_DME_mr, color=C_EMERALD, linewidth=2.0, label="MR (NaA)")
ax_b.plot(z_mm, Y_DME_tr, color=C_RED,     linewidth=2.0, linestyle="--", label="TR (no membrane)")
ax_b.set_title("DME Yield", fontsize=9.5, color=C_SLATE)
_fmt(ax_b, "Y$_{DME}$  [%]", ylim=[0, 105])
ax_b.text(z_mm[-1]*0.95, res_mr["Y_DME"] + 2,
          f"{res_mr['Y_DME']:.1f}%", fontsize=8, color=C_EMERALD, ha="right")
ax_b.text(z_mm[-1]*0.95, res_tr["Y_DME"] - 5,
          f"{res_tr['Y_DME']:.1f}%", fontsize=8, color=C_RED, ha="right")

# Panel C: Water Molar Flow (retentate)
ax_c = axes[1, 0]
F_H2O_mr_mmol = F_mr[IDX["H2O"], :] * 1e3   # mol/s → mmol/s
F_H2O_tr_mmol = F_tr[IDX["H2O"], :] * 1e3
F_H2O_perm_mmol = F_perm[IDX["H2O"], :] * 1e3
ax_c.plot(z_mm, F_H2O_mr_mmol,   color=C_BLUE,    linewidth=2.0, label="MR retentate H₂O")
ax_c.plot(z_mm, F_H2O_tr_mmol,   color=C_SLATE,   linewidth=2.0, linestyle="--", label="TR H₂O")
ax_c.plot(z_mm, F_H2O_perm_mmol, color=C_SKY,     linewidth=1.5, linestyle="-.", label="MR permeate H₂O (cumulative)")
ax_c.set_title("H₂O Molar Flow Rate", fontsize=9.5, color=C_SLATE)
_fmt(ax_c, "$\\dot{n}_{H_2O}$  [mmol s⁻¹]")

# Panel D: CH3OH and DME molar flows
ax_d = axes[1, 1]
F_meoh_mr_mmol = F_mr[IDX["CH3OH"], :] * 1e3
F_dme_mr_mmol  = F_mr[IDX["DME"],   :] * 1e3
F_meoh_tr_mmol = F_tr[IDX["CH3OH"], :] * 1e3
F_dme_tr_mmol  = F_tr[IDX["DME"],   :] * 1e3
ax_d.plot(z_mm, F_meoh_mr_mmol, color=C_GOLD,  linewidth=2.0, label="MR CH₃OH")
ax_d.plot(z_mm, F_dme_mr_mmol,  color=C_EMERALD, linewidth=2.0, label="MR DME")
ax_d.plot(z_mm, F_meoh_tr_mmol, color=C_GOLD,  linewidth=2.0, linestyle="--", label="TR CH₃OH")
ax_d.plot(z_mm, F_dme_tr_mmol,  color=C_RED,   linewidth=2.0, linestyle="--", label="TR DME")
ax_d.set_title("Methanol & DME Molar Flows", fontsize=9.5, color=C_SLATE)
_fmt(ax_d, "$\\dot{n}$  [mmol s⁻¹]")

out_ax = os.path.join(FIGURES_DIR, "dme_cfd_axial_profiles.png")
fig2.savefig(out_ax, dpi=300, bbox_inches="tight", facecolor="white")
plt.close(fig2)
print(f"  Saved: {out_ax}")

# ===========================================================================
# Print summary
# ===========================================================================
print("\n" + "="*62)
print("SIMULATION RESULTS — Case Study B: Shell-Packed CMR (NaA)")
print("="*62)
print(f"  CO2 Conversion (MR):        {res_mr['X_CO2']:.2f} %")
print(f"  CO2 Conversion (TR):        {res_tr['X_CO2']:.2f} %")
print(f"  DME Yield     (MR):         {res_mr['Y_DME']:.2f} %")
print(f"  DME Yield     (TR):         {res_tr['Y_DME']:.2f} %")
print(f"  DME Selectivity (MR):       {res_mr['S_DME']:.2f} %")
print(f"  H2O Removed (MR):           {res_mr['water_removed_pct']:.2f} %")
print(f"  Carbon Balance Error (MR):  {res_mr['carbon_balance_error']:.2e}")
print("="*62)
print("\nFigures written to figures/:")
print("  dme_cfd_3d_flow.png")
print("  dme_cfd_axial_profiles.png")
