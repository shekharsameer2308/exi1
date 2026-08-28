import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

print("Generating heatmaps...")

# ==========================================
# 1. Reactor Thermal Profile Heatmap (1D)
# ==========================================
df_prof = pd.read_csv('outputs/membrane_reactor_profiles.csv')

fig, (ax_heat, ax_lines) = plt.subplots(2, 1, figsize=(10, 6), gridspec_kw={'height_ratios': [1, 5]})

# Temperature Heatmap (1D strip)
Z = df_prof['temperature_k'].values.reshape(1, -1)
extent = [df_prof['z_m'].min(), df_prof['z_m'].max(), 0, 1]
im = ax_heat.imshow(Z, aspect='auto', cmap='inferno', extent=extent)
ax_heat.set_yticks([])
ax_heat.set_xlabel('Reactor Length, z (m)')
ax_heat.set_title('Reactor Internal Temperature Heatmap (K)', pad=10)
fig.colorbar(im, ax=ax_heat, fraction=0.05, pad=0.04, label='Temperature (K)')

# Species concentration lines below it
ax_lines.plot(df_prof['z_m'], df_prof['CO2'], label='CO2', color='#1f77b4', lw=2.5)
ax_lines.plot(df_prof['z_m'], df_prof['H2'], label='H2', color='#d62728', lw=2.5)
ax_lines.plot(df_prof['z_m'], df_prof['MeOH'], label='Methanol', color='#2ca02c', lw=2.5)
ax_lines.plot(df_prof['z_m'], df_prof['H2O'], label='Water', color='#17becf', lw=2.5)

ax_lines.set_xlabel('Reactor Length, z (m)')
ax_lines.set_ylabel('Molar Flow Rate (mol/s)')
ax_lines.legend(loc='center right')
ax_lines.grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
plt.savefig('outputs/reactor_thermal_heatmap.png', dpi=300)
plt.close()


# ==========================================
# 2. Statistical Correlation Heatmap
# ==========================================
df_doe = pd.read_csv('outputs/membrane_doe.csv')

# Select key variables
cols = [
    'inlet_temperature_k', 'inlet_pressure_bar', 'inlet_flow_mol_s', 
    'h2_co2_ratio', 'water_permeance_mol_m2_s_pa', 'co2_conversion', 
    'methanol_selectivity_carbon', 'methanol_sty_kg_m3cat_h'
]
corr = df_doe[cols].corr()

plt.figure(figsize=(10, 8))
sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", vmin=-1, vmax=1, 
            cbar_kws={'label': 'Pearson Correlation'})
plt.title('Predictive Data Correlation Heatmap', pad=15)
plt.tight_layout()
plt.savefig('outputs/data_correlation_heatmap.png', dpi=300)
plt.close()

print("Heatmaps saved to outputs/")
