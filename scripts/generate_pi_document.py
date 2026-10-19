"""
generate_pi_document.py
=======================
Generates a standalone, publication-grade HTML and PDF technical report
specifically for the Process Intensification (PI) Analysis and Architecture
Comparison (Single-Tube vs. Four-Tube Shell-Packed CMR).
"""

import os
import sys
import subprocess
import shutil

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUTPUT_HTML = os.path.join(ROOT_DIR, "PROCESS_INTENSIFICATION_ANALYSIS.html")
OUTPUT_PDF = os.path.join(ROOT_DIR, "PROCESS_INTENSIFICATION_ANALYSIS.pdf")
ARTIFACT_DIR = "/Users/sameershekhar/.gemini/antigravity/brain/1a40eeba-2407-43f4-a37f-6ecea5ebeeae"

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Process Intensification Analysis: Intensified Direct CO2-to-DME Multi-Tube Catalytic Membrane Reactors</title>
<script>
window.MathJax = {
  tex: {
    inlineMath: [['$', '$'], ['\\(', '\\)']],
    displayMath: [['$$', '$$'], ['\\[', '\\]']],
    processEscapes: true
  },
  options: {
    renderActions: {
      addMenu: []
    }
  }
};
</script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>
<style>
  @page {
    size: A4;
    margin: 12mm 14mm 12mm 14mm;
  }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #1e293b;
    background-color: #ffffff;
    line-height: 1.5;
    margin: 0;
    padding: 15px;
  }
  .container {
    max-width: 1000px;
    margin: 0 auto;
  }
  h1 {
    font-size: 22px;
    font-weight: 700;
    color: #0f172a;
    border-bottom: 3px solid #10b981;
    padding-bottom: 8px;
    margin-bottom: 6px;
    text-align: center;
  }
  .subtitle {
    text-align: center;
    font-size: 12.5px;
    color: #475569;
    margin-bottom: 16px;
  }
  .metadata-badge {
    display: inline-block;
    background: #f1f5f9;
    padding: 4px 10px;
    border-radius: 4px;
    font-size: 11.5px;
    color: #334155;
    margin: 0 4px;
    border: 1px solid #cbd5e1;
  }
  h2 {
    font-size: 18px;
    font-weight: 600;
    color: #1e293b;
    border-left: 4px solid #10b981;
    padding-left: 10px;
    margin-top: 30px;
    margin-bottom: 14px;
  }
  h3 {
    font-size: 15px;
    font-weight: 600;
    color: #334155;
    margin-top: 20px;
    margin-bottom: 10px;
  }
  p, li {
    font-size: 13px;
    color: #334155;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 16px 0;
    font-size: 12px;
    page-break-inside: avoid;
    break-inside: avoid;
  }
  th, td {
    padding: 8px 10px;
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
  .callout {
    background-color: #f8fafc;
    border-left: 4px solid #475569;
    padding: 12px 16px;
    margin: 16px 0;
    border-radius: 0 4px 4px 0;
    font-size: 12.5px;
  }
  .callout-success {
    background-color: #f0fdf4;
    border-left: 4px solid #10b981;
    color: #166534;
  }
  pre {
    background-color: #0f172a;
    color: #f8fafc;
    padding: 10px 14px;
    border-radius: 6px;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    font-size: 10.5px;
    overflow-x: auto;
    line-height: 1.4;
    page-break-inside: avoid;
    break-inside: avoid;
  }
  @media print {
    body {
      padding: 0;
    }
    .page-break {
      page-break-before: always;
    }
  }
</style>
</head>
<body>
<div class="container">

  <h1>Process Intensification Analysis: Intensified Direct CO₂-to-DME Multi-Tube Catalytic Membrane Reactors</h1>
  <div class="subtitle">
    Comprehensive Chemical Reaction Engineering (CRE) Analysis & Architecture Evaluation<br>
    <span class="metadata-badge">Operating Regime: 250 °C, 40 bar</span>
    <span class="metadata-badge">Catalyst: Cu/ZnO/Al₂O₃ + H-ZSM-5</span>
    <span class="metadata-badge">Membrane: Hydrophilic NaA Zeolite</span>
    <span class="metadata-badge">Verification: 34/34 Tests Passed</span>
  </div>

  <h2>1. Executive Summary & Process Intensification Scorecard</h2>
  <p>
    Chemical Process Intensification (PI) is defined by the European Roadmap for Process Intensification (2007) and Keil (2018) as:
  </p>
  <div class="callout callout-success">
    <em>"A set of radically innovative principles in process and equipment design that can bring significant (<strong>greater than a factor of 2</strong>) benefits in terms of process and chain efficiency, capital and operating expenses, quality, waste, and process safety."</em>
  </div>
  <p>
    By coupling direct DME synthesis with selective in-situ water extraction across hydrophilic NaA zeolite membranes inside a four-tube shell-packed bed, this technology delivers a true paradigm shift over conventional packed-bed reactors (PBR) and overcomes the thermodynamic Gibbs equilibrium barrier.
  </p>

  <table>
    <thead>
      <tr>
        <th>Process Metric</th>
        <th>Traditional Packed Bed (PBR)</th>
        <th>Gibbs Equilibrium Ceiling</th>
        <th>Single Centre Tube CMR</th>
        <th>Four-Tube Shell-Packed CMR (Case B)</th>
        <th>Process Intensification Factor / Gain</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>CO₂ Conversion (\(X_{\text{CO}_2}\))</strong></td>
        <td>34.90%</td>
        <td>48.71%</td>
        <td>93.62%</td>
        <td class="highlight-cell"><strong>96.26%</strong></td>
        <td><strong>+175.8%</strong> (2.76× vs. PBR)<br><strong>+97.6%</strong> (1.98× vs. Gibbs)</td>
      </tr>
      <tr>
        <td><strong>DME Single-Pass Yield (\(Y_{\text{DME}}\))</strong></td>
        <td>31.17%</td>
        <td>46.54%</td>
        <td>91.94%</td>
        <td class="highlight-cell"><strong>94.28%</strong></td>
        <td><strong>+202.5%</strong> (3.02× vs. PBR)<br><strong>+102.6%</strong> (2.03× vs. Gibbs)</td>
      </tr>
      <tr>
        <td><strong>DME Carbon Selectivity (\(S_{\text{DME}}\))</strong></td>
        <td>89.29%</td>
        <td>95.55%</td>
        <td>98.21%</td>
        <td class="highlight-cell"><strong>97.94%</strong></td>
        <td><strong>+8.65 pp</strong> vs. PBR</td>
      </tr>
      <tr>
        <td><strong>In-Situ Water Removal (\(f_{\text{H}_2\text{O,rem}}\))</strong></td>
        <td>0.00%</td>
        <td>0.00%</td>
        <td>99.11%</td>
        <td class="highlight-cell"><strong>99.70%</strong></td>
        <td><strong>+99.70 pp</strong> extraction</td>
      </tr>
      <tr>
        <td><strong>Specific Membrane Area (\(a_v\))</strong></td>
        <td>0.0 m⁻¹</td>
        <td>—</td>
        <td>133.33 m⁻¹</td>
        <td class="highlight-cell"><strong>266.67 m⁻¹</strong></td>
        <td><strong>2.0× increase</strong> (+100%)</td>
      </tr>
      <tr>
        <td><strong>Maximum Diffusion Distance (\(L\))</strong></td>
        <td>5.64 mm</td>
        <td>—</td>
        <td>5.00 mm</td>
        <td class="highlight-cell"><strong>2.50 mm</strong></td>
        <td><strong>50.0% reduction</strong> vs. Single Tube</td>
      </tr>
      <tr>
        <td><strong>Characteristic Diffusion Time (\(t_D \sim L^2/D\))</strong></td>
        <td>~31.8 / D</td>
        <td>—</td>
        <td>~25.0 / D</td>
        <td class="highlight-cell"><strong>~6.25 / D</strong></td>
        <td><strong>4.0× faster transport</strong> (75% drop in \(t_D\))</td>
      </tr>
      <tr>
        <td><strong>Reactor Space-Time Yield (STY)</strong></td>
        <td>1.0× (Ref)</td>
        <td>1.49×</td>
        <td>2.95×</td>
        <td class="highlight-cell"><strong>3.02×</strong></td>
        <td><strong>67% reactor volume reduction</strong></td>
      </tr>
      <tr>
        <td><strong>Recycle Gas Recompression Duty</strong></td>
        <td>65.1% of feed</td>
        <td>51.3% of feed</td>
        <td>6.4% of feed</td>
        <td class="highlight-cell"><strong>3.7% of feed</strong></td>
        <td><strong>>85% reduction</strong> in recycle load</td>
      </tr>
      <tr>
        <td><strong>Evaluation Latency per Point</strong></td>
        <td>~2.5 s (BDF ODE)</td>
        <td>—</td>
        <td>—</td>
        <td class="highlight-cell"><strong><0.2 ms</strong></td>
        <td><strong>≈ 12,500× digital speedup</strong></td>
      </tr>
    </tbody>
  </table>

  <div class="page-break"></div>

  <h2>2. Theoretical Foundations & The Four Guiding Principles of PI</h2>
  <p>
    Following the framework established by Van Gerven and Stankiewicz (2009) and reviewed by Keil (2018), Process Intensification is grounded in four core physical principles:
  </p>

  <h3>2.1 Principle 1: Maximize the Effectiveness of Intra- and Intermolecular Events</h3>
  <p>
    In direct DME synthesis over \(\text{Cu/ZnO/Al}_2\text{O}_3\), water byproduct competitively adsorbs onto active copper sites, represented by the denominator \(D_k^3\) in the Langmuir-Hinshelwood kinetic expression:
  </p>
  $$r_{\text{CO}_2} = \frac{k_1 p_{\text{CO}_2} p_{\text{H}_2} \left[ 1 - \frac{p_{\text{H}_2\text{O}} p_{\text{CH}_3\text{OH}}}{K_{eq1} p_{\text{H}_2}^3 p_{\text{CO}_2}} \right]}{D_k^3}$$
  $$D_k = 1 + K_{\text{H}_2\text{O},\text{H}_2}\left(\frac{p_{\text{H}_2\text{O}}}{p_{\text{H}_2}}\right) + \sqrt{K_{\text{H}_2} p_{\text{H}_2}} + K_{\text{H}_2\text{O}} p_{\text{H}_2\text{O}}$$
  <p>
    By continuously extracting \(99.70\%\) of the generated water through the membrane wall, local water partial pressure is depressed to \(p_{\text{H}_2\text{O}} \le 0.15\text{ bar}\). Consequently, \(D_k \approx 1\), preventing active-site blocking and sustaining peak forward rates along the entire bed length.
  </p>

  <h3>2.2 Principle 2: Give All Molecules the Same Processing Experience</h3>
  <p>
    In un-intensified or maldistributed packed beds, fluid packets near impermeable reactor walls experience stagnation and high byproduct concentrations, while core flows bypass reactive zones. 
    In the Four-Tube Shell-Packed CMR, four membrane sinks are placed symmetrically at half the shell radius (\(R_{\text{pitch}} = 5.0\text{ mm} = R_{\text{shell}}/2\)). 3D Darcy-Brinkman continuum CFD simulations confirm that radial suction velocity vectors converge uniformly into the four tubes, preventing wall channeling and ensuring every fluid tracer shares a uniform concentration and residence-time history.
  </p>

  <h3>2.3 Principle 3: Optimize Driving Forces and Maximize Specific Surface Area</h3>
  <p>
    Transport rates scale directly with driving force and specific area:
  </p>
  $$Q = U A \Delta T, \quad N_A = k_L a_v \Delta C, \quad J_{\text{perm}} = \Pi_{\text{H}_2\text{O}} \Delta p_{\text{H}_2\text{O}}$$
  <p>
    To maximize the volumetric mass transfer rate \(J_{\text{vol}} = J_{\text{perm}} \cdot a_v\), the four-tube architecture reduces tube diameter from \(10.0\text{ mm}\) to \(5.0\text{ mm}\), doubling specific surface area from \(a_v = 133.3\text{ m}^{-1}\) to <strong>\(266.7\text{ m}^{-1}\)</strong>.
    Furthermore, the characteristic diffusion time scales quadratically with diffusion length:
  </p>
  $$t_D \approx \frac{L^2}{D_{\text{eff}}}$$
  <p>
    Reducing the maximum diffusion path from \(5.00\text{ mm}\) down to \(2.50\text{ mm}\) decreases the diffusion time by an exact factor of 4 (<strong>\(75\%\) reduction</strong>).
  </p>

  <h3>2.4 Principle 4: Maximize Synergies from Partial Processes (Multifunctional Reactors)</h3>
  <p>
    Rather than executing synthesis in a reactor, condensation in a flash drum, and separation in downstream distillation columns, the Catalytic Membrane Reactor combines chemical reaction and separation in one apparatus. Removing the product \(\text{H}_2\text{O}\) as it forms suppresses the reverse reaction quotient (\(Q_1 \ll K_{eq1}\)), shifting chemical equilibrium toward stoichiometric conversion.
  </p>

  <h2>3. Why We Intensified: Technical & Thermodynamic Bottlenecks</h2>
  <ul>
    <li><strong>Equilibrium Barrier:</strong> Classical packed-bed direct synthesis is capped at 34.90% single-pass conversion (48.71% Gibbs ceiling at 250 °C, 40 bar) due to Le Chatelier back-reaction from water accumulation.</li>
    <li><strong>Active Site Deactivation:</strong> Elevated steam partial pressures cause hydrothermal dealumination of H-ZSM-5 acid sites and accelerate copper sintering.</li>
    <li><strong>Downstream Recompression & Distillation Duty:</strong> With &gt;65% unreacted syngas per pass, conventional plants require massive recompression recycle loops and multi-column distillation systems to break the ternary methanol-water-DME mixture.</li>
  </ul>

  <h2>4. How We Intensified: Engineering Design & CRE Mechanics</h2>
  <ul>
    <li><strong>Bifunctional Bed:</strong> Cu/ZnO/Al₂O₃ + H-ZSM-5 (dp = 0.30 mm, bulk density 1200 kg/m³, bed voidage 0.40).</li>
    <li><strong>Hydrophilic NaA Zeolite:</strong> 4.0 Å pore size, highly permeable to water (kinetic diameter 2.65 Å) while strictly rejecting DME (4.30 Å), with selectivities \(\alpha(\text{H}_2\text{O}/\text{DME}) \ge 10,000\), \(\alpha(\text{H}_2\text{O}/\text{CO}_2) \ge 5000\), and \(\alpha(\text{H}_2\text{O}/\text{H}_2) \ge 1000\).</li>
    <li><strong>Damköhler Permeation Synchronization:</strong> Operates at \(Da_{\text{perm}} = \frac{r_{\text{gen,H}_2\text{O}}}{J_{\text{perm,H}_2\text{O}} \cdot a_v} \approx 1\) at \(\text{GHSV} \approx 1000\text{ h}^{-1}\).</li>
  </ul>

  <div class="page-break"></div>

  <h2>5. Architectural Comparison: Single-Tube vs. Four-Tube Shell-Packed CMR</h2>

  <table>
    <thead>
      <tr>
        <th>Architectural Feature</th>
        <th>Single Centre Tube CMR</th>
        <th>Four-Tube Shell-Packed CMR (Case B)</th>
        <th>Physical Consequence / CRE Advantage</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Membrane Tube Layout</strong></td>
        <td>1 central tube</td>
        <td class="highlight-cell"><strong>4 distributed tubes</strong></td>
        <td>Symmetric multi-sink radial suction.</td>
      </tr>
      <tr>
        <td><strong>Membrane Outer Diameter (\(d_t\))</strong></td>
        <td>10.0 mm</td>
        <td class="highlight-cell"><strong>5.0 mm</strong></td>
        <td>Halving tube diameter doubles surface area density (\(a_v \propto 1/d\)).</td>
      </tr>
      <tr>
        <td><strong>Pitch Circle Radius (\(R_{\text{pitch}}\))</strong></td>
        <td>0.0 mm (centered)</td>
        <td class="highlight-cell"><strong>5.0 mm (\(R_{\text{shell}} / 2\))</strong></td>
        <td>Tubes placed at (5,0), (0,5), (-5,0), (0,-5) mm.</td>
      </tr>
      <tr>
        <td><strong>Shell Bore Diameter (\(D_{\text{shell}}\))</strong></td>
        <td>20.0 mm</td>
        <td class="highlight-cell"><strong>20.0 mm</strong></td>
        <td>Identical vessel outer boundary.</td>
      </tr>
      <tr>
        <td><strong>Active Catalyst Bed Area (\(A_c\))</strong></td>
        <td>2.3562 cm² (75.0%)</td>
        <td class="highlight-cell"><strong>2.3562 cm² (75.0%)</strong></td>
        <td><strong>Identical catalyst volume and catalyst mass</strong>.</td>
      </tr>
      <tr>
        <td><strong>Specific Membrane Area (\(a_v\))</strong></td>
        <td>133.33 m⁻¹</td>
        <td class="highlight-cell"><strong>266.67 m⁻¹</strong></td>
        <td><strong>+100% (2.0× increase)</strong> in interfacial area density.</td>
      </tr>
      <tr>
        <td><strong>Max Diffusion Distance to Wall (\(L\))</strong></td>
        <td>5.00 mm</td>
        <td class="highlight-cell"><strong>2.50 mm</strong></td>
        <td><strong>50.0% reduction</strong> in maximum transport distance.</td>
      </tr>
      <tr>
        <td><strong>Characteristic Diffusion Time (\(t_D \sim L^2/D\))</strong></td>
        <td>~25.0 / D</td>
        <td class="highlight-cell"><strong>~6.25 / D</strong></td>
        <td><strong>4× faster mass transport</strong> (75% reduction in \(t_D\)).</td>
      </tr>
      <tr>
        <td><strong>Clearance Between Tubes</strong></td>
        <td>—</td>
        <td class="highlight-cell"><strong>2.071 mm</strong></td>
        <td>\(\delta / d_p = 6.9 \ge 5.0\); stable random packing without bridging.</td>
      </tr>
      <tr>
        <td><strong>Clearance to Outer Wall</strong></td>
        <td>5.00 mm</td>
        <td class="highlight-cell"><strong>2.50 mm</strong></td>
        <td>\(\delta / d_p = 8.3 \ge 5.0\); prevents wall bridging.</td>
      </tr>
      <tr>
        <td><strong>Dead Zones / Unsealed Voids</strong></td>
        <td>Zero</td>
        <td class="highlight-cell"><strong>Zero (100% shell packing)</strong></td>
        <td>No unsealed voids; zero bypass risk.</td>
      </tr>
      <tr>
        <td><strong>Single-Pass CO₂ Conversion (\(X_{\text{CO}_2}\))</strong></td>
        <td>93.62%</td>
        <td class="highlight-cell"><strong>96.26%</strong></td>
        <td><strong>+2.64 pp</strong> higher conversion.</td>
      </tr>
      <tr>
        <td><strong>Single-Pass DME Yield (\(Y_{\text{DME}}\))</strong></td>
        <td>91.94%</td>
        <td class="highlight-cell"><strong>94.28%</strong></td>
        <td><strong>+2.34 pp</strong> higher single-pass yield.</td>
      </tr>
      <tr>
        <td><strong>DME Carbon Selectivity (\(S_{\text{DME}}\))</strong></td>
        <td>98.21%</td>
        <td class="highlight-cell"><strong>97.94%</strong></td>
        <td>High selectivity maintained (&gt;97.9%).</td>
      </tr>
      <tr>
        <td><strong>In-Situ Water Removal (\(f_{\text{H}_2\text{O,rem}}\))</strong></td>
        <td>99.11%</td>
        <td class="highlight-cell"><strong>99.70%</strong></td>
        <td>Enhanced extraction halo across 4 sinks.</td>
      </tr>
    </tbody>
  </table>

  <div class="page-break"></div>

  <h3>5.1 The Physical Mechanism of Four-Tube Superiority</h3>
  <ol>
    <li>
      <strong>Quadratic Diffusion Scaling (\(t_D \sim L^2/D\)):</strong> In the single-tube CMR, water generated near the outer shell must diffuse across a thick 5.0 mm annular layer, establishing a steep radial concentration gradient (\(p_{\text{H}_2\text{O}} \approx 0.4\text{--}0.6\text{ bar}\) at the wall). In the four-tube CMR, the maximum diffusion distance is capped at 2.50 mm, slashing diffusion time by 75% (\(t_D \sim (2.5/5.0)^2 = 0.25\)).
    </li>
    <li>
      <strong>Doubled Interfacial Area at Constant Catalyst Bed Volume:</strong> Because both reactors maintain \(A_c = 2.356\text{ cm}^2\) (75% shell volume), splitting the membrane into four 5.0 mm tubes doubles the total perimeter from \(10\pi\text{ mm}\) to \(20\pi\text{ mm}\), elevating \(a_v\) from 133.3 to 266.7 m⁻¹.
    </li>
    <li>
      <strong>Elimination of Wall Channeling:</strong> The 3D Darcy-Brinkman CFD model shows that four distributed suction sinks draw gas radially inward, suppressing wall voidage bypass and establishing uniform plug-flow behavior across the entire bed.
    </li>
  </ol>

  <h2>6. Digital Process Intensification via Machine Learning Surrogates</h2>
  <p>
    Solving the 1D stiff BDF ODE boundary value problem requires ~2.5 seconds per point. An ExtraTrees ensemble surrogate was trained on 120 validated physics simulations:
  </p>
  <ul>
    <li><strong>Predictive Fidelity (Held-Out Test Set):</strong> \(R^2 = 0.867\text{--}0.884\), \(\text{MAE} \le 2.14\%\), \(\text{MAPE} \le 2.91\%\) across all target variables.</li>
    <li><strong>Inference Speedup:</strong> Latency reduced from 2.5 s to &lt;0.2 ms (<strong>≈ 12,500× acceleration</strong>), enabling real-time multi-objective design optimization.</li>
  </ul>

  <h2>7. Conclusions</h2>
  <p>
    The Four-Tube Shell-Packed CMR satisfies the European Roadmap criterion for Process Intensification by achieving a <strong>3.02× single-pass DME yield increase</strong> (31.17% to 94.28%), bypassing the Gibbs equilibrium ceiling (46.54%), slashing reactor footprint by 67%, and reducing downstream recycle duty by &gt;85%.
  </p>

</div>
</body>
</html>
"""

def main():
    print("Writing HTML document...")
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(HTML_TEMPLATE)
    print(f"Generated HTML: {OUTPUT_HTML} ({os.path.getsize(OUTPUT_HTML)/1024:.1f} KB)")

    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    if os.path.exists(chrome_path):
        print("Compiling PDF via headless Chrome...")
        cmd = [
            chrome_path,
            "--headless",
            "--disable-gpu",
            "--run-all-compositor-stages-before-draw",
            "--virtual-time-budget=8000",
            "--no-pdf-header-footer",
            f"--print-to-pdf={OUTPUT_PDF}",
            OUTPUT_HTML,
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0 and os.path.exists(OUTPUT_PDF):
            pdf_size_kb = os.path.getsize(OUTPUT_PDF) / 1024
            print(f"Generated PDF: {OUTPUT_PDF} ({pdf_size_kb:.1f} KB)")
            
            # Copy to brain artifact directory
            artifact_pdf = os.path.join(ARTIFACT_DIR, "PROCESS_INTENSIFICATION_ANALYSIS.pdf")
            shutil.copyfile(OUTPUT_PDF, artifact_pdf)
            print(f"Copied to Artifacts: {artifact_pdf}")
            
            # Copy to user Downloads folder
            downloads_pdf = os.path.expanduser("~/Downloads/PROCESS_INTENSIFICATION_ANALYSIS.pdf")
            shutil.copyfile(OUTPUT_PDF, downloads_pdf)
            print(f"Copied to Downloads: {downloads_pdf}")
        else:
            print(f"Error generating PDF: {res.stderr}")
    else:
        print("Google Chrome not found; HTML document available.")

if __name__ == "__main__":
    main()
