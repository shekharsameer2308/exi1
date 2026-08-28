import pandas as pd
import numpy as np

print("Generating analytical results...")

# 1. Load Data
doe_df = pd.read_csv('outputs/membrane_doe.csv')
summary_df = pd.read_csv('outputs/reactor_case_summary.csv')

# 2. Analytical Results: Correlations (What drives performance?)
corr = doe_df.corr(numeric_only=True)
corr_targets = corr[['methanol_sty_kg_m3cat_h', 'co2_conversion', 'methanol_selectivity_carbon']]

# 3. Best Operating Conditions (Top 10 by Methanol Production)
top10 = doe_df.sort_values('methanol_sty_kg_m3cat_h', ascending=False).head(10)

# 4. Statistical Summary
stats = doe_df.describe().T

# 5. Write everything to a beautifully formatted Excel sheet
excel_path = 'outputs/Reactor_Analysis_Report.xlsx'
with pd.ExcelWriter(excel_path) as writer:
    summary_df.to_excel(writer, sheet_name='PBR_vs_Membrane', index=False)
    top10.to_excel(writer, sheet_name='Top_10_Optimum_Conditions', index=False)
    stats.to_excel(writer, sheet_name='Statistical_Summary')
    corr_targets.to_excel(writer, sheet_name='Key_Correlations')
    doe_df.to_excel(writer, sheet_name='Full_DOE_Data', index=False)

print("Saved report to", excel_path)

# 6. Output key insights for the chat
print("\n--- KEY ANALYTICAL INSIGHTS ---")
print("1. Maximum CO2 Conversion Achieved:", f"{doe_df['co2_conversion'].max()*100:.2f}%")
print("2. Maximum Methanol STY Achieved:", f"{doe_df['methanol_sty_kg_m3cat_h'].max():.2f} kg/m3/h")
print("3. Strongest Correlation with Methanol Production (STY):")
print(corr['methanol_sty_kg_m3cat_h'].sort_values(ascending=False).head(4))
print("4. Strongest Correlation with CO2 Conversion:")
print(corr['co2_conversion'].sort_values(ascending=False).head(4))
