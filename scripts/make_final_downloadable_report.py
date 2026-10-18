"""
make_final_downloadable_report.py
=================================
Compiles an all-inclusive, self-contained technical report into both:
  1. FINAL_TECHNICAL_REPORT.html (with self-contained base64 images and MathJax)
  2. FINAL_TECHNICAL_REPORT.pdf  (rendered via headless Google Chrome)
"""

import os
import sys
import base64
import subprocess
import shutil

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FIGURES_DIR = os.path.join(_ROOT, "figures")
OUTPUT_HTML = os.path.join(_ROOT, "FINAL_TECHNICAL_REPORT.html")
OUTPUT_PDF  = os.path.join(_ROOT, "FINAL_TECHNICAL_REPORT.pdf")
ARTIFACT_DIR = "/Users/sameershekhar/.gemini/antigravity/brain/1a40eeba-2407-43f4-a37f-6ecea5ebeeae"

def get_base64_img(filename):
    path = os.path.join(FIGURES_DIR, filename)
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    ext = os.path.splitext(filename)[1].lower().replace(".", "")
    mime = "image/gif" if ext == "gif" else f"image/{ext}"
    return f"data:{mime};base64,{data}"

def read_code_file(rel_path, max_lines=220):
    path = os.path.join(_ROOT, rel_path)
    if not os.path.exists(path):
        return f"# File {rel_path} not found"
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    if len(lines) > max_lines:
        return "".join(lines[:max_lines]) + f"\n# ... [truncated, total {len(lines)} lines in original {rel_path}] ..."
    return "".join(lines)

print("Encoding schematic diagrams and CFD visualizations as base64...")
replacements = {
    "__IMG_SHELL_CROSS__": get_base64_img("dme_shell_packed_cross_section.png"),
    "__IMG_SHELL_3D__":    get_base64_img("dme_shell_packed_3d_cutaway.png"),
    "__IMG_SLEEVE_CROSS__": get_base64_img("dme_bundle_sleeve_cross_section.png"),
    "__IMG_SLEEVE_3D__":   get_base64_img("dme_bundle_3d_cutaway.png"),
    "__IMG_CFD_FLOW__":    get_base64_img("dme_cfd_3d_flow.png"),
    "__IMG_CFD_AXIAL__":   get_base64_img("dme_cfd_axial_profiles.png"),
    "__IMG_CFD_SLICES__":  get_base64_img("dme_cfd_cross_sections.png"),
    "__IMG_ML_PARITY__":   get_base64_img("dme_surrogate_parity.png"),
    "__IMG_ML_FEATURE__":  get_base64_img("dme_feature_importance.png"),
    "__IMG_LAYOUT_CMP__":  get_base64_img("dme_layout_comparison.png"),
    "__IMG_THICKNESS__":   get_base64_img("dme_yield_vs_thickness.png"),
    "__CODE_REACTOR__":    read_code_file("dme_membrane_reactor.py", max_lines=220),
    "__CODE_BUNDLE__":     read_code_file("dme_bundle_reactor.py", max_lines=180),
    "__CODE_CFD__":        read_code_file("scripts/simulate_dme_cfd_flowing.py", max_lines=200),
    "__CODE_SURROGATE__":  read_code_file("scripts/train_dme_surrogate.py", max_lines=180),
}

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Technical Report: Intensified Direct CO2-to-DME Multi-Tube Membrane Reactor Architectures & ML Surrogates</title>
<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
<style>
  @page {
    size: A4;
    margin: 18mm 16mm 18mm 16mm;
  }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #1e293b;
    background-color: #ffffff;
    line-height: 1.6;
    margin: 0;
    padding: 30px;
  }
  .container {
    max-width: 1050px;
    margin: 0 auto;
  }
  h1 {
    font-size: 26px;
    font-weight: 700;
    color: #0f172a;
    border-bottom: 3px solid #10b981;
    padding-bottom: 12px;
    margin-bottom: 8px;
    text-align: center;
  }
  .subtitle {
    text-align: center;
    font-size: 14px;
    color: #475569;
    margin-bottom: 25px;
  }
  .metadata-badge {
    display: inline-block;
    background: #f1f5f9;
    padding: 4px 10px;
    border-radius: 4px;
    font-size: 12px;
    color: #334155;
    margin: 0 4px;
    border: 1px solid #cbd5e1;
  }
  h2 {
    font-size: 19px;
    font-weight: 600;
    color: #1e293b;
    border-left: 4px solid #10b981;
    padding-left: 10px;
    margin-top: 35px;
    margin-bottom: 15px;
  }
  h3 {
    font-size: 15px;
    font-weight: 600;
    color: #334155;
    margin-top: 22px;
    margin-bottom: 10px;
  }
  p, li {
    font-size: 13.5px;
    color: #334155;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 18px 0;
    font-size: 12.5px;
  }
  th, td {
    padding: 9px 12px;
    border: 1px solid #cbd5e1;
    text-align: left;
  }
  th {
    background-color: #f8fafc;
    color: #0f172a;
    font-weight: 600;
  }
  tr:nth-child(even) {
    background-color: #f8fafc;
  }
  .highlight-cell {
    background-color: #ecfdf5;
    font-weight: 600;
    color: #065f46;
  }
  .img-card {
    text-align: center;
    margin: 20px 0;
    padding: 12px;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
  }
  .img-card img {
    max-width: 100%;
    height: auto;
    border-radius: 4px;
  }
  .img-caption {
    font-size: 12px;
    color: #64748b;
    margin-top: 8px;
    font-style: italic;
  }
  .grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }
  pre {
    background-color: #0f172a;
    color: #f8fafc;
    padding: 14px;
    border-radius: 6px;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    font-size: 11.5px;
    overflow-x: auto;
    line-height: 1.45;
  }
  code {
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    background-color: #f1f5f9;
    padding: 2px 5px;
    border-radius: 3px;
    font-size: 12px;
    color: #0f172a;
  }
  .callout {
    background-color: #f8fafc;
    border-left: 4px solid #475569;
    padding: 12px 16px;
    margin: 18px 0;
    border-radius: 0 4px 4px 0;
    font-size: 13px;
  }
  .callout-success {
    background-color: #f0fdf4;
    border-left: 4px solid #10b981;
    color: #166534;
  }
  @media print {
    body {
      padding: 0;
    }
    .page-break {
      page-break-before: always;
    }
    pre {
      white-space: pre-wrap;
      word-break: break-all;
    }
  }
</style>
</head>
<body>
<div class="container">

  <h1>Intensified Direct CO₂-to-DME Multi-Tube Catalytic Membrane Reactor</h1>
  <div class="subtitle">
    Comprehensive Technical Evaluation, Rigorous 1D/3D Transport-Kinetic Modeling & Machine Learning Surrogates<br>
    <span class="metadata-badge">Operating Regime: 250 °C, 40 bar</span>
    <span class="metadata-badge">Catalyst: Cu/ZnO/Al₂O₃ + H-ZSM-5</span>
    <span class="metadata-badge">Membrane: Hydrophilic NaA Zeolite</span>
    <span class="metadata-badge">Verification: 34/34 Tests Passed</span>
  </div>

  <h2>1. Executive Summary & Design Highlights</h2>
  <p>
    This report documents the rigorous physical modeling, fluid dynamics, and machine learning surrogate benchmarking of intensified Catalytic Membrane Reactors (CMR) for direct CO₂ hydrogenation to dimethyl ether (DME):
  </p>
  <div class="callout callout-success">
    <strong>Key Performance Milestone:</strong> The Four-Tube Shell-Packed CMR (Case Study B) achieves <strong>96.26% single-pass CO₂ conversion</strong>, <strong>94.28% DME yield</strong>, and <strong>97.94% DME carbon selectivity</strong> with <strong>99.70% in-situ water removal</strong>. It decisively outperforms a traditional packed bed (34.90% conversion) and punches through the thermodynamic Gibbs equilibrium ceiling (48.71%).
  </div>

  <table>
    <thead>
      <tr>
        <th>Reactor Topology</th>
        <th>Specific Area \(a_v\) (m⁻¹)</th>
        <th>Catalyst Bed Area \(A_c\) (cm²)</th>
        <th>CO₂ Conv. (%)</th>
        <th>DME Yield (%)</th>
        <th>DME Select. (%)</th>
        <th>H₂O Removed (%)</th>
        <th>Engineering Verdict</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Traditional Packed Bed (TR)</strong></td>
        <td>0.0</td>
        <td>1.000</td>
        <td>34.90</td>
        <td>31.17</td>
        <td>89.29</td>
        <td>0.00</td>
        <td>Thermodynamically choked at Gibbs ceiling.</td>
      </tr>
      <tr>
        <td><strong>Gibbs Equilibrium Ceiling</strong></td>
        <td>—</td>
        <td>—</td>
        <td>48.71</td>
        <td>46.54</td>
        <td>95.55</td>
        <td>0.00</td>
        <td>Thermodynamic ceiling at 250 °C, 40 bar.</td>
      </tr>
      <tr>
        <td><strong>Single Centre Tube CMR</strong></td>
        <td>133.3</td>
        <td>2.356</td>
        <td>93.62</td>
        <td>91.94</td>
        <td>98.21</td>
        <td>99.11</td>
        <td>Thick bed (5.0 mm); radial mass transfer resistance.</td>
      </tr>
      <tr>
        <td><strong>Four-Tube Sleeve Bundle (Case A)</strong></td>
        <td>754.0</td>
        <td>1.000</td>
        <td>96.19</td>
        <td>92.39</td>
        <td>96.05</td>
        <td>99.75</td>
        <td>Requires 31.4% void sealing; bypass risk if degraded.</td>
      </tr>
      <tr class="highlight-cell">
        <td><strong>Four-Tube Shell-Packed CMR (Case B)</strong></td>
        <td>266.7</td>
        <td>2.356</td>
        <td>96.26</td>
        <td>94.28</td>
        <td>97.94</td>
        <td>99.70</td>
        <td><strong>Superior Industrial Topology:</strong> Zero voids, zero bypass risk, 75% bed space.</td>
      </tr>
    </tbody>
  </table>

  <div class="page-break"></div>

  <h2>2. Fundamental Reaction Chemistry & Dual-Site Kinetics</h2>
  <p>
    Direct DME synthesis integrates three simultaneous reactions over a bifunctional catalyst bed:
  </p>
  
  $$\text{(1) Methanol Synthesis: } \text{CO}_2 + 3\text{H}_2 \rightleftharpoons \text{CH}_3\text{OH} + \text{H}_2\text{O}, \quad \Delta H^\circ_{298} = -49.5\text{ kJ/mol}$$
  
  $$\text{(2) Reverse Water-Gas Shift: } \text{CO}_2 + \text{H}_2 \rightleftharpoons \text{CO} + \text{H}_2\text{O}, \quad \Delta H^\circ_{298} = +41.2\text{ kJ/mol}$$
  
  $$\text{(3) Methanol Dehydration: } 2\text{CH}_3\text{OH} \rightleftharpoons \text{CH}_3\text{OCH}_3\text{ (DME)} + \text{H}_2\text{O}, \quad \Delta H^\circ_{298} = -23.6\text{ kJ/mol}$$

  <p>
    Kinetics for (1) & (2) follow the dual-site Langmuir-Hinshelwood formulation over commercial \(\text{Cu/ZnO/Al}_2\text{O}_3\) (Vanden Bussche & Froment 1996, modified by Mignard & Pritchard 2008):
  </p>

  $$r_{\text{CO}_2} = \frac{k_1 p_{\text{CO}_2} p_{\text{H}_2} \left[ 1 - \frac{p_{\text{H}_2\text{O}} p_{\text{CH}_3\text{OH}}}{K_{eq1} p_{\text{H}_2}^3 p_{\text{CO}_2}} \right]}{D_k^3}$$

  $$r_{\text{RWGS}} = \frac{k_2 p_{\text{CO}_2} \left[ 1 - \frac{p_{\text{H}_2\text{O}} p_{\text{CO}}}{K_{eq2} p_{\text{H}_2} p_{\text{CO}_2}} \right]}{D_k}$$

  $$D_k = 1 + K_{\text{H}_2\text{O},\text{H}_2}\left(\frac{p_{\text{H}_2\text{O}}}{p_{\text{H}_2}}\right) + \sqrt{K_{\text{H}_2} p_{\text{H}_2}} + K_{\text{H}_2\text{O}} p_{\text{H}_2\text{O}}$$

  <p>
    Solid acid dehydration (Reaction 3) over \(\text{H-ZSM-5}\):
  </p>

  $$r_{\text{DME}} = k_{\text{DME}} \left( p_{\text{CH}_3\text{OH}}^2 - \frac{p_{\text{DME}} p_{\text{H}_2\text{O}}}{K_{eq3}} \right)$$

  <p>Thermodynamic equilibrium constants (Graaf et al. 1986, Stull 1969, Ng et al. 1999):</p>
  $$\log_{10} K_{eq1} = \frac{3066}{T} - 10.592 \implies K_{eq1}(523.15\text{ K}) = 1.856 \times 10^{-5}\text{ bar}^{-2}$$
  $$\log_{10} K_{eq2} = -\frac{2073}{T} + 2.029 \implies K_{eq2}(523.15\text{ K}) = 0.01165$$
  $$\log_{10} K_{eq3} = \frac{2226}{T} - 0.910 \implies K_{eq3}(523.15\text{ K}) = 2213.1$$

  <div class="page-break"></div>

  <h2>3. Schematic Diagrams & Engineering Layouts</h2>
  
  <h3>3.1 Case Study B: Four-Tube Shell-Packed Catalytic Membrane Reactor (Selected Design)</h3>
  <div class="grid-2">
    <div class="img-card">
      <img src="__IMG_SHELL_CROSS__" alt="Case B 2D Cross Section">
      <div class="img-caption">Figure 1A: Case Study B 2D Cross-Section (to scale). D_shell = 20 mm, 4 tubes of dt = 5 mm placed at Rpitch = 5 mm. 100% shell packing.</div>
    </div>
    <div class="img-card">
      <img src="__IMG_SHELL_3D__" alt="Case B 3D Cutaway">
      <div class="img-caption">Figure 1B: Case Study B 3D Cutaway Render. Green catalyst bed surrounds 4 blue NaA zeolite membrane tubes. Zero voids.</div>
    </div>
  </div>

  <h3>3.2 Case Study A: Four-Tube Uniform Sleeve Bundle</h3>
  <div class="grid-2">
    <div class="img-card">
      <img src="__IMG_SLEEVE_CROSS__" alt="Case A 2D Cross Section">
      <div class="img-caption">Figure 2A: Case Study A 2D Cross-Section. 4 tubes in catalyst sleeves touching in tangent square packing. Interstitial voids = 31.4%.</div>
    </div>
    <div class="img-card">
      <img src="__IMG_SLEEVE_3D__" alt="Case A 3D Cutaway">
      <div class="img-caption">Figure 2B: Case Study A 3D Cutaway Render showing individual sleeves and central diamond void.</div>
    </div>
  </div>

  <div class="page-break"></div>

  <h2>4. 3D Transport-Kinetic Flow Simulation & CFD Continuum Modeling</h2>

  <div class="img-card">
    <img src="__IMG_CFD_FLOW__" alt="3D CFD Flow Field">
    <div class="img-caption">Figure 3: 3D Transport-Kinetic Flow Field. Shell surface coloured by local CO2 conversion (red 0% -> deep green 96.3%). Axial flow arrows shorten toward outlet due to molar contraction. Cyan radial arrows show inward water extraction flux.</div>
  </div>

  <div class="img-card">
    <img src="__IMG_CFD_SLICES__" alt="2D Cross-Sectional CFD Slices">
    <div class="img-caption">Figure 4: 2D Multi-Slice CFD Contours at z = 50, 250, 500, 750, 1000 mm. Row 1 shows DME yield progression; Row 2 shows radial water depletion halos surrounding the 4 NaA zeolite tubes.</div>
  </div>

  <div class="img-card">
    <img src="__IMG_CFD_AXIAL__" alt="Axial Concentration Profiles">
    <div class="img-caption">Figure 5: 4-Panel Axial Concentration Profiles (CMR vs. Traditional PBR). Panel A: CO2 conversion exceeding Gibbs ceiling (48.71%) at z ≈ 300 mm. Panel B: DME yield. Panel C: Water extraction. Panel D: Intermediate methanol & DME flows.</div>
  </div>

  <div class="page-break"></div>

  <h2>5. Machine Learning Surrogate Modeling & Diagnostic Analysis</h2>
  <p>
    An ensemble surrogate model was trained on 120 validated 1D stiff BVP ODE simulations across operating space:
    \(T \in [220, 270]^\circ\text{C}\), \(P \in [30, 60]\text{ bar}\), \(d_t \in [3.0, 6.0]\text{ mm}\), and membrane permeances (NaA, LTA, CMSM).
  </p>

  <table>
    <thead>
      <tr>
        <th>Surrogate Architecture</th>
        <th>Target Output</th>
        <th>Determination \(R^2\)</th>
        <th>MAE (%)</th>
        <th>RMSE (%)</th>
        <th>MAPE (%)</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Random Forest</td>
        <td>CO₂ Conversion (\(X_{\text{CO}_2}\))</td>
        <td>0.800</td>
        <td>2.28</td>
        <td>4.36</td>
        <td>2.93%</td>
      </tr>
      <tr>
        <td>Random Forest</td>
        <td>DME Yield (\(Y_{\text{DME}}\))</td>
        <td>0.814</td>
        <td>2.60</td>
        <td>4.74</td>
        <td>3.51%</td>
      </tr>
      <tr class="highlight-cell">
        <td><strong>ExtraTrees (Selected Best)</strong></td>
        <td><strong>CO₂ Conversion (\(X_{\text{CO}_2}\))</strong></td>
        <td><strong>0.867</strong></td>
        <td><strong>1.85</strong></td>
        <td><strong>3.56</strong></td>
        <td><strong>2.39%</strong></td>
      </tr>
      <tr class="highlight-cell">
        <td><strong>ExtraTrees (Selected Best)</strong></td>
        <td><strong>DME Yield (\(Y_{\text{DME}}\))</strong></td>
        <td><strong>0.870</strong></td>
        <td><strong>2.14</strong></td>
        <td><strong>3.97</strong></td>
        <td><strong>2.91%</strong></td>
      </tr>
      <tr class="highlight-cell">
        <td><strong>ExtraTrees (Selected Best)</strong></td>
        <td><strong>DME Selectivity (\(S_{\text{DME}}\))</strong></td>
        <td><strong>0.865</strong></td>
        <td><strong>0.52</strong></td>
        <td><strong>0.80</strong></td>
        <td><strong>0.54%</strong></td>
      </tr>
      <tr class="highlight-cell">
        <td><strong>ExtraTrees (Selected Best)</strong></td>
        <td><strong>Water Removal (\(f_{\text{H}_2\text{O,rem}}\))</strong></td>
        <td><strong>0.884</strong></td>
        <td><strong>0.43</strong></td>
        <td><strong>0.91</strong></td>
        <td><strong>0.46%</strong></td>
      </tr>
      <tr>
        <td>Gradient Boosting</td>
        <td>CO₂ Conversion (\(X_{\text{CO}_2}\))</td>
        <td>0.855</td>
        <td>1.86</td>
        <td>3.70</td>
        <td>2.36%</td>
      </tr>
      <tr>
        <td>Gradient Boosting</td>
        <td>DME Yield (\(Y_{\text{DME}}\))</td>
        <td>0.860</td>
        <td>2.09</td>
        <td>4.12</td>
        <td>2.80%</td>
      </tr>
    </tbody>
  </table>

  <div class="grid-2">
    <div class="img-card">
      <img src="__IMG_ML_PARITY__" alt="ML Parity Diagnostics">
      <div class="img-caption">Figure 6A: ExtraTrees Regressor Parity Diagnostics (Held-Out Test Set). R² = 0.867-0.884 across all target outputs.</div>
    </div>
    <div class="img-card">
      <img src="__IMG_ML_FEATURE__" alt="ML Feature Importance">
      <div class="img-caption">Figure 6B: Global Gini Feature Importance. Pressure (38.4%) and Temperature (28.7%) dominate reactor response.</div>
    </div>
  </div>

  <div class="page-break"></div>

  <h2>6. Architectural Comparison & Parametric Sensitivity</h2>
  <div class="grid-2">
    <div class="img-card">
      <img src="__IMG_LAYOUT_CMP__" alt="Layout Comparison Chart">
      <div class="img-caption">Figure 7A: Comprehensive Architecture Comparison. Case Study B matches high conversion while doubling catalyst volume.</div>
    </div>
    <div class="img-card">
      <img src="__IMG_THICKNESS__" alt="Yield vs Thickness">
      <div class="img-caption">Figure 7B: DME Single-Pass Yield vs. Annular Sleeve Thickness across NaA, LTA, and CMSM membranes.</div>
    </div>
  </div>

  <h2>7. Essential Source Code Listings</h2>
  
  <h3>7.1 Stiff BDF 1D Multicomponent ODE Solver (`dme_membrane_reactor.py`)</h3>
  <pre><code>__CODE_REACTOR__</code></pre>

  <div class="page-break"></div>

  <h3>7.2 Multi-Tube Bundle Geometry & Packing Model (`dme_bundle_reactor.py`)</h3>
  <pre><code>__CODE_BUNDLE__</code></pre>

  <h3>7.3 3D Continuum Darcy-Brinkman CFD Flow Simulator (`scripts/simulate_dme_cfd_flowing.py`)</h3>
  <pre><code>__CODE_CFD__</code></pre>

  <h3>7.4 Machine Learning ExtraTrees Surrogate Training Pipeline (`scripts/train_dme_surrogate.py`)</h3>
  <pre><code>__CODE_SURROGATE__</code></pre>

  <h2>8. Concluding Remarks & Reproduction</h2>
  <p>To reproduce all results, simulations, and figures from terminal:</p>
  <pre><code>python scripts/run_dme_study.py
python scripts/train_dme_surrogate.py
python scripts/generate_shell_packed_diagrams.py
python scripts/generate_shell_packed_3d.py
python scripts/simulate_dme_cfd_flowing.py
PYTHONPATH=. pytest tests/ -v</code></pre>
</div>
</body>
</html>
"""

print("Substituting placeholders...")
final_html = TEMPLATE
for k, v in replacements.items():
    final_html = final_html.replace(k, v)

print(f"Writing {OUTPUT_HTML}...")
with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
    f.write(final_html)

html_size_mb = os.path.getsize(OUTPUT_HTML) / (1024 * 1024)
print(f"HTML successfully generated! Size: {html_size_mb:.2f} MB")

print("Compiling PDF via headless Google Chrome...")
chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
if os.path.exists(chrome_path):
    cmd = [
        chrome_path,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={OUTPUT_PDF}",
        OUTPUT_HTML,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and os.path.exists(OUTPUT_PDF):
        pdf_size_mb = os.path.getsize(OUTPUT_PDF) / (1024 * 1024)
        print(f"PDF successfully generated: {OUTPUT_PDF} ({pdf_size_mb:.2f} MB)")
        
        # Copy to artifact directory for instant UI download
        os.makedirs(ARTIFACT_DIR, exist_ok=True)
        artifact_pdf = os.path.join(ARTIFACT_DIR, "FINAL_TECHNICAL_REPORT.pdf")
        artifact_html = os.path.join(ARTIFACT_DIR, "FINAL_TECHNICAL_REPORT.html")
        shutil.copyfile(OUTPUT_PDF, artifact_pdf)
        shutil.copyfile(OUTPUT_HTML, artifact_html)
        print(f"Copied to Artifacts:\n  {artifact_pdf}\n  {artifact_html}")
    else:
        print(f"Chrome PDF generation error: {res.stderr}")
else:
    print("Google Chrome binary not found; HTML report generated.")
