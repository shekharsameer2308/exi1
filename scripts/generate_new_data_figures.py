import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

from dme_bundle_reactor import bundle_layout
from dme_membrane_reactor import run_dme_simulation, solve_gibbs_equilibrium

os.makedirs('/Users/sameershekhar/Documents/GitHub/p1/figures', exist_ok=True)
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

# Palette
COLOR_SLATE = '#475569'
COLOR_EMERALD = '#10b981'
COLOR_RED = '#ef4444'
COLOR_GRAY = '#6b7280'
COLOR_NAVY = '#1e293b'
COLOR_AMBER = '#d97706'
COLOR_BLUE = '#2563eb'

# ==============================================================================
# FIGURE 1: TECHNICAL DIMENSION & GEOMETRY CROSS-SECTIONS
# ==============================================================================
print("Generating Figure 1: Technical Dimensions & Geometry Cross-Sections...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7.5), dpi=300)

# Shell: R = 10 mm, D = 20 mm
R_shell = 10.0 # mm

for ax in (ax1, ax2):
    ax.set_xlim(-12.5, 12.5)
    ax.set_ylim(-12.5, 12.5)
    ax.set_aspect('equal')
    ax.axis('off')

# --- AX1: Single-Tube Benchmark CMR ---
# Outer Shell Wall
circle_shell_1 = plt.Circle((0, 0), R_shell, edgecolor=COLOR_NAVY, facecolor='#f8fafc', linewidth=2.5)
ax1.add_patch(circle_shell_1)

# Catalyst Bed (Annulus)
annulus_cat = plt.Circle((0, 0), R_shell, edgecolor=COLOR_SLATE, facecolor='#e2e8f0', alpha=0.85, hatch='///', linewidth=1.5)
ax1.add_patch(annulus_cat)

# Membrane Outer Diameter (dt = 10 mm, rt = 5 mm)
circle_mem_1 = plt.Circle((0, 0), 5.0, edgecolor=COLOR_EMERALD, facecolor='#ccfbf1', linewidth=2.0)
ax1.add_patch(circle_mem_1)

# Membrane Inner Lumen (din = 8 mm, rin = 4 mm)
circle_lum_1 = plt.Circle((0, 0), 4.0, edgecolor='#0f766e', facecolor='#ffffff', linewidth=1.5)
ax1.add_patch(circle_lum_1)

# Dimension Lines & Annotations for AX1
# Shell diameter: D = 20 mm
ax1.annotate('', xy=(-R_shell, -11.5), xytext=(R_shell, -11.5),
             arrowprops=dict(arrowstyle='<->', color=COLOR_NAVY, lw=1.5))
ax1.text(0, -12.2, r'Shell Outer Bore: $D_{\mathrm{shell}} = 20.00\ \mathrm{mm}$', ha='center', va='top', fontsize=11, fontweight='bold', color=COLOR_NAVY)

# Membrane Tube: dt = 10 mm
ax1.annotate('', xy=(-5.0, 0), xytext=(5.0, 0),
             arrowprops=dict(arrowstyle='<->', color='#0f766e', lw=1.5))
ax1.text(0, 0.4, r'$d_t = 10.0\ \mathrm{mm}$', ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#0f766e')

# Annular bed thickness dr = 5.0 mm
ax1.annotate('', xy=(5.0, 6.0), xytext=(10.0, 6.0),
             arrowprops=dict(arrowstyle='<->', color=COLOR_SLATE, lw=1.5))
ax1.text(7.5, 6.4, r'$\Delta r = 5.00\ \mathrm{mm}$', ha='center', va='bottom', fontsize=9.5, fontweight='bold', color=COLOR_SLATE)

ax1.text(0, 8.0, r'Catalyst Bed (Annular)' + '\n' + r'$A_c = 2.3562\ \mathrm{cm}^2$' + '\n' + r'($75\%$ of bore)',
         ha='center', va='center', fontsize=9.5, color=COLOR_NAVY, bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor=COLOR_SLATE, alpha=0.9))

ax1.text(0, -2.0, r'Sweep Lumen' + '\n' + r'$d_{\mathrm{in}} = 8.0\ \mathrm{mm}$', ha='center', va='center', fontsize=8.5, color='#0f766e')

ax1.set_title("Model 1: Single-Tube Benchmark CMR\nSpecific Area: $a_v = 133.33\ \mathrm{m}^{-1}$", fontsize=13, fontweight='bold', color=COLOR_NAVY, pad=12)

# --- AX2: Four-Tube Shell-Packed CMR (Case Study B) ---
# Outer Shell Wall
circle_shell_2 = plt.Circle((0, 0), R_shell, edgecolor=COLOR_NAVY, facecolor='#f8fafc', linewidth=2.5)
ax2.add_patch(circle_shell_2)

# Packed Bed (100% of Shell around tubes)
bed_packed = plt.Circle((0, 0), R_shell, edgecolor=COLOR_SLATE, facecolor='#e2e8f0', alpha=0.85, hatch='///', linewidth=1.5)
ax2.add_patch(bed_packed)

# 4 Membrane Tubes: dt = 5.0 mm (rt = 2.5 mm) at R_pitch = 5.0 mm
pitch_centers = [(5.0, 0.0), (0.0, 5.0), (-5.0, 0.0), (0.0, -5.0)]

# Pitch circle (dashed)
pitch_circle = plt.Circle((0, 0), 5.0, edgecolor=COLOR_GRAY, facecolor='none', linestyle='--', linewidth=1.0)
ax2.add_patch(pitch_circle)

for idx, (cx, cy) in enumerate(pitch_centers):
    # Tube outer
    t_out = plt.Circle((cx, cy), 2.5, edgecolor=COLOR_EMERALD, facecolor='#ccfbf1', linewidth=1.8)
    ax2.add_patch(t_out)
    # Tube inner lumen (din = 3.4 mm, rin = 1.7 mm)
    t_in = plt.Circle((cx, cy), 1.7, edgecolor='#0f766e', facecolor='#ffffff', linewidth=1.2)
    ax2.add_patch(t_in)
    ax2.text(cx, cy, f"T{idx+1}", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#0f766e')

# Dimension Lines & Annotations for AX2
ax2.annotate('', xy=(-R_shell, -11.5), xytext=(R_shell, -11.5),
             arrowprops=dict(arrowstyle='<->', color=COLOR_NAVY, lw=1.5))
ax2.text(0, -12.2, r'Shell Outer Bore: $D_{\mathrm{shell}} = 20.00\ \mathrm{mm}$', ha='center', va='top', fontsize=11, fontweight='bold', color=COLOR_NAVY)

# Pitch circle annotation
ax2.annotate(r'$R_{\mathrm{pitch}} = 5.00\ \mathrm{mm}$' + '\n' + r'($R_{\mathrm{shell}}/2$)',
             xy=(3.535, 3.535), xytext=(8.0, 8.5),
             arrowprops=dict(arrowstyle='->', color=COLOR_GRAY, lw=1.2),
             fontsize=9, color=COLOR_NAVY, bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor=COLOR_GRAY, alpha=0.9))

# Wall Clearance (2.5 mm)
ax2.annotate('', xy=(7.5, 0), xytext=(10.0, 0),
             arrowprops=dict(arrowstyle='<->', color=COLOR_RED, lw=1.5))
ax2.text(8.75, 0.4, r'$2.50\ \mathrm{mm}$' + '\n(Wall gap)', ha='center', va='bottom', fontsize=8.5, fontweight='bold', color=COLOR_RED)

# Centerline Clearance (2.5 mm)
ax2.annotate('', xy=(0, 0), xytext=(0, 2.5),
             arrowprops=dict(arrowstyle='<->', color=COLOR_RED, lw=1.5))
ax2.text(0.3, 1.25, r'$2.50\ \mathrm{mm}$' + '\n(Center gap)', ha='left', va='center', fontsize=8.5, fontweight='bold', color=COLOR_RED)

# Inter-tube diagonal gap (2.071 mm)
ax2.annotate('', xy=(3.232, 1.768), xytext=(1.768, 3.232),
             arrowprops=dict(arrowstyle='<->', color=COLOR_AMBER, lw=1.5))
ax2.text(2.6, 2.7, r'$\delta_{\mathrm{gap}} = 2.071\ \mathrm{mm}$' + '\n' + r'($\delta/d_p = 6.90 \geq 5$)',
         ha='left', va='bottom', fontsize=8.5, fontweight='bold', color=COLOR_AMBER)

ax2.text(0, -7.5, r'Packed Catalyst Bed' + '\n' + r'$A_c = 2.3562\ \mathrm{cm}^2$' + '\n' + r'Zero Voids / No Bypass',
         ha='center', va='center', fontsize=9.5, color=COLOR_NAVY, bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor=COLOR_SLATE, alpha=0.9))

ax2.set_title("Model 2: Four-Tube Shell-Packed CMR\nSpecific Area: $a_v = 266.67\ \mathrm{m}^{-1}$ (2.0x Intensification)", fontsize=13, fontweight='bold', color=COLOR_NAVY, pad=12)

plt.tight_layout()
fig_path_1 = '/Users/sameershekhar/Documents/GitHub/p1/figures/dme_reactor_architectures_dimensions.png'
plt.savefig(fig_path_1, dpi=300)
plt.close()
print(f"Saved: {fig_path_1}")

# ==============================================================================
# FIGURE 2: MULTI-ARCHITECTURE PERFORMANCE COMPARISON (LU KINETICS)
# ==============================================================================
print("\nGenerating Figure 2: Layout Performance Comparison Chart...")
single_geo = bundle_layout(catalyst='centre_tube', d=0.010, D_shell=0.020, L=1.0)
four_geo = bundle_layout(catalyst='shell_packed', d=0.005, D_shell=0.020, L=1.0)

res_tr = run_dme_simulation(single_geo, is_membrane=False)
res_single = run_dme_simulation(single_geo, membrane_type='NaA', is_membrane=True)
res_four = run_dme_simulation(four_geo, membrane_type='NaA', is_membrane=True)
gibbs = solve_gibbs_equilibrium(T_K=523.15, P_bar=40.0)

labels = ['Traditional Bed (TR)', 'Gibbs Limit', 'Single-Tube CMR', 'Four-Tube CMR (Case B)']
X_CO2 = [res_tr['X_CO2'], gibbs['X_CO2_eq'], res_single['X_CO2'], res_four['X_CO2']]
Y_DME = [res_tr['Y_DME'], gibbs['Y_DME_eq'], res_single['Y_DME'], res_four['Y_DME']]
S_DME = [res_tr['S_DME'], gibbs['S_DME_eq'], res_single['S_DME'], res_four['S_DME']]
W_rem = [res_tr['water_removed_pct'], 0.0, res_single['water_removed_pct'], res_four['water_removed_pct']]

x = np.arange(len(labels))
width = 0.20

fig, ax = plt.subplots(figsize=(12, 6.5), dpi=300)

rects1 = ax.bar(x - 1.5*width, X_CO2, width, label=r'$\mathrm{CO}_2$ Conversion ($X_{\mathrm{CO}_2}$)', color=COLOR_SLATE)
rects2 = ax.bar(x - 0.5*width, Y_DME, width, label=r'DME Single-Pass Yield ($Y_{\mathrm{DME}}$)', color=COLOR_EMERALD)
rects3 = ax.bar(x + 0.5*width, S_DME, width, label=r'DME Selectivity ($S_{\mathrm{DME}}$)', color=COLOR_BLUE)
rects4 = ax.bar(x + 1.5*width, W_rem, width, label=r'In-Situ Water Removed ($f_{\mathrm{H}_2\mathrm{O,rem}}$)', color=COLOR_AMBER)

ax.set_ylabel('Percentage (%)', fontsize=12, fontweight='bold', color=COLOR_NAVY)
ax.set_title('Catalytic Membrane Reactor Intensification Benchmark\n(T = 250 °C, P = 40 bar, H₂/CO₂ = 3.0, GHSV = 1000 h⁻¹, Lu et al. 2004 Kinetics)', fontsize=13, fontweight='bold', color=COLOR_NAVY, pad=14)
ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=10.5, fontweight='bold', color=COLOR_NAVY)
ax.legend(frameon=True, facecolor='white', edgecolor=COLOR_SLATE, fontsize=10, loc='upper left')
ax.set_ylim(0, 115)

def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        if height > 0:
            ax.annotate(f'{height:.1f}%',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=8, fontweight='bold', color=COLOR_NAVY)

autolabel(rects1)
autolabel(rects2)
autolabel(rects3)
autolabel(rects4)

# Threshold reference line for Gibbs equilibrium ceiling
ax.axhline(gibbs['Y_DME_eq'], color=COLOR_RED, linestyle='--', linewidth=1.5, alpha=0.7)
ax.text(0.1, gibbs['Y_DME_eq'] + 1.5, f'Thermodynamic Equilibrium Ceiling (DME Yield = {gibbs["Y_DME_eq"]:.1f}%)', color=COLOR_RED, fontsize=9.5, fontweight='bold')

plt.tight_layout()
fig_path_2 = '/Users/sameershekhar/Documents/GitHub/p1/figures/dme_layout_comparison.png'
plt.savefig(fig_path_2, dpi=300)
plt.close()
print(f"Saved: {fig_path_2}")

# ==============================================================================
# FIGURE 3: AXIAL CONCENTRATION PROFILES (Z = 0 TO 1.0 M)
# ==============================================================================
print("\nGenerating Figure 3: Axial Concentration Profiles...")
z = np.array(res_four['z'])
ret_four = np.array(res_four['profiles_ret']) # 6 x N
ret_single = np.array(res_single['profiles_ret'])

P_tot_bar = 40.0
# Partial pressures = F_i / sum(F_i) * P_tot
p_ret_four = (ret_four / np.sum(ret_four, axis=0)) * P_tot_bar
p_ret_single = (ret_single / np.sum(ret_single, axis=0)) * P_tot_bar

fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(14, 6), dpi=300, sharey=True)

species_names = [r'$\mathrm{CO}_2$', r'$\mathrm{H}_2$', r'$\mathrm{H}_2\mathrm{O}$', r'$\mathrm{CH}_3\mathrm{OH}$', r'$\mathrm{CO}$', r'$\mathrm{DME}$']
species_colors = [COLOR_SLATE, COLOR_BLUE, COLOR_AMBER, '#8b5cf6', COLOR_RED, COLOR_EMERALD]

# Single-Tube
for sp_idx in range(6):
    ax_a.plot(z, p_ret_single[sp_idx, :], label=species_names[sp_idx], color=species_colors[sp_idx], lw=2.2)

ax_a.set_title('Model 1: Single-Tube Benchmark CMR\n($a_v = 133.33\\ \\mathrm{m}^{-1}, \\Delta r = 5.0\\ \\mathrm{mm}$)', fontsize=12, fontweight='bold', color=COLOR_NAVY)
ax_a.set_xlabel('Axial Reactor Position $z$ (m)', fontsize=11, fontweight='bold', color=COLOR_NAVY)
ax_a.set_ylabel('Partial Pressure (bar)', fontsize=11, fontweight='bold', color=COLOR_NAVY)
ax_a.legend(loc='center right', frameon=True, fontsize=9.5)
ax_a.grid(True, linestyle=':', alpha=0.6)

# Four-Tube
for sp_idx in range(6):
    ax_b.plot(z, p_ret_four[sp_idx, :], label=species_names[sp_idx], color=species_colors[sp_idx], lw=2.2)

ax_b.set_title('Model 2: Four-Tube Shell-Packed CMR\n($a_v = 266.67\\ \\mathrm{m}^{-1}, \\Delta r_{\\max} = 2.5\\ \\mathrm{mm}$)', fontsize=12, fontweight='bold', color=COLOR_NAVY)
ax_b.set_xlabel('Axial Reactor Position $z$ (m)', fontsize=11, fontweight='bold', color=COLOR_NAVY)
ax_b.legend(loc='center right', frameon=True, fontsize=9.5)
ax_b.grid(True, linestyle=':', alpha=0.6)

plt.suptitle('Axial Species Partial Pressure Profiles Along Catalyst Bed\n(Rapid In-Situ Water Depletion Drives DME Synthesis to Completion)', fontsize=13, fontweight='bold', color=COLOR_NAVY)
plt.tight_layout()
fig_path_3 = '/Users/sameershekhar/Documents/GitHub/p1/figures/dme_cfd_axial_profiles.png'
plt.savefig(fig_path_3, dpi=300)
plt.close()
print(f"Saved: {fig_path_3}")

# ==============================================================================
# FIGURE 4: RETRAINING MACHINE LEARNING SURROGATE & GENERATING PARITY PLOTS
# ==============================================================================
print("\nGenerating Training Dataset & Retraining ExtraTrees ML Surrogate on Lu Kinetics...")

# Parameter space sampling
np.random.seed(42)
N_SAMPLES = 120

T_samples = np.random.uniform(220.0, 270.0, N_SAMPLES)
P_samples = np.random.uniform(30.0, 60.0, N_SAMPLES)
GHSV_samples = np.random.uniform(500.0, 2500.0, N_SAMPLES)
mem_types = np.random.choice(['NaA', 'LTA', 'CMSM'], N_SAMPLES)
layouts = np.random.choice(['single', 'four'], N_SAMPLES)

X_data = []
Y_targets = [] # [X_CO2, Y_DME, S_DME, W_rem]

for idx in range(N_SAMPLES):
    T_val = float(T_samples[idx])
    P_val = float(P_samples[idx])
    ghsv_val = float(GHSV_samples[idx])
    m_type = str(mem_types[idx])
    l_type = str(layouts[idx])
    
    geo = single_geo if l_type == 'single' else four_geo
    
    # Feature vector: [T, P, GHSV, av, Pi_H2O]
    pi_h2o = 1.8e-7 if m_type == 'NaA' else (2.0e-7 if m_type == 'LTA' else 0.6e-7)
    av_val = geo['a_v']
    
    res = run_dme_simulation(
        geo,
        membrane_type=m_type,
        is_membrane=True,
        T_C=T_val,
        P_ret_bar=P_val,
        GHSV_h=ghsv_val
    )
    
    X_data.append([T_val, P_val, ghsv_val, av_val, pi_h2o])
    Y_targets.append([res['X_CO2'], res['Y_DME'], res['S_DME'], res['water_removed_pct']])

X_mat = np.array(X_data)
Y_mat = np.array(Y_targets)

# Train/Test Split (80/20)
X_train, X_test, Y_train, Y_test = train_test_split(X_mat, Y_mat, test_size=0.20, random_state=42)

# Fit ExtraTrees Regressor
model_et = ExtraTreesRegressor(n_estimators=100, random_state=42)
model_et.fit(X_train, Y_train)
Y_pred = model_et.predict(X_test)

# Evaluate Metrics
target_labels = [r'$\mathrm{CO}_2$ Conversion ($X_{\mathrm{CO}_2}$)', r'DME Yield ($Y_{\mathrm{DME}}$)', r'DME Selectivity ($S_{\mathrm{DME}}$)', r'Water Removed ($f_{\mathrm{H}_2\mathrm{O,rem}}$)']

fig, axes = plt.subplots(2, 2, figsize=(12, 11), dpi=300)
axes = axes.flatten()

for t_idx in range(4):
    ax = axes[t_idx]
    y_true = Y_test[:, t_idx]
    y_p = Y_pred[:, t_idx]
    
    r2 = r2_score(y_true, y_p)
    mae = mean_absolute_error(y_true, y_p)
    rmse = np.sqrt(mean_squared_error(y_true, y_p))
    
    min_val = min(np.min(y_true), np.min(y_p)) - 2.0
    max_val = max(np.max(y_true), np.max(y_p)) + 2.0
    
    ax.scatter(y_true, y_p, color=COLOR_BLUE, edgecolors=COLOR_NAVY, s=50, alpha=0.8, zorder=3)
    ax.plot([min_val, max_val], [min_val, max_val], color=COLOR_RED, linestyle='--', lw=1.8, label='1:1 Parity')
    
    ax.set_xlim(min_val, max_val)
    ax.set_ylim(min_val, max_val)
    ax.set_xlabel(f'True Physics ODE Value (%)', fontsize=10.5, fontweight='bold', color=COLOR_NAVY)
    ax.set_ylabel(f'ExtraTrees Predicted Value (%)', fontsize=10.5, fontweight='bold', color=COLOR_NAVY)
    ax.set_title(target_labels[t_idx], fontsize=11.5, fontweight='bold', color=COLOR_NAVY)
    
    # Metrics box
    textstr = f'$R^2 = {r2:.3f}$\n$\mathrm{{MAE}} = {mae:.2f}\\%$\n$\mathrm{{RMSE}} = {rmse:.2f}\\%$'
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=9.5,
            verticalalignment='top', bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=COLOR_SLATE, alpha=0.9))
    ax.grid(True, linestyle=':', alpha=0.6)

plt.suptitle('ExtraTrees Surrogate Model Parity Benchmark on Held-Out Test Set\n(Trained on Multi-Component ODE Simulations with Lu et al. 2004 Kinetics)', fontsize=13, fontweight='bold', color=COLOR_NAVY)
plt.tight_layout()
fig_path_4 = '/Users/sameershekhar/Documents/GitHub/p1/figures/dme_surrogate_parity.png'
plt.savefig(fig_path_4, dpi=300)
plt.close()
print(f"Saved: {fig_path_4}")

# ==============================================================================
# FIGURE 5: GLOBAL FEATURE IMPORTANCE
# ==============================================================================
print("\nGenerating Figure 5: Feature Importance Ranking...")
feature_names = ['Temperature ($T$)', 'Pressure ($P$)', 'Space Velocity (GHSV)', 'Specific Area ($a_v$)', 'Water Permeance ($\Pi_{\mathrm{H}_2\mathrm{O}}$)']
importances = model_et.feature_importances_
indices = np.argsort(importances)[::-1]

fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)
bars = ax.barh(range(len(importances)), importances[indices], color=COLOR_SLATE, edgecolor=COLOR_NAVY, height=0.6)
ax.set_yticks(range(len(importances)))
ax.set_yticklabels([feature_names[i] for i in indices], fontsize=10.5, fontweight='bold', color=COLOR_NAVY)
ax.set_xlabel('Gini Feature Importance Fraction', fontsize=11, fontweight='bold', color=COLOR_NAVY)
ax.set_title('Global Sensitivity Analysis: Key Drivers of Direct DME Synthesis\n(ExtraTrees Impurity Reduction)', fontsize=12.5, fontweight='bold', color=COLOR_NAVY, pad=12)
ax.set_xlim(0, max(importances) * 1.2)

for bar in bars:
    w = bar.get_width()
    ax.text(w + 0.008, bar.get_y() + bar.get_height()/2, f'{w*100:.1f}%', va='center', fontsize=9.5, fontweight='bold', color=COLOR_NAVY)

plt.tight_layout()
fig_path_5 = '/Users/sameershekhar/Documents/GitHub/p1/figures/dme_feature_importance.png'
plt.savefig(fig_path_5, dpi=300)
plt.close()
print(f"Saved: {fig_path_5}")

print("\nALL 5 PUBLICATION FIGURES SUCCESSFULLY GENERATED!")
