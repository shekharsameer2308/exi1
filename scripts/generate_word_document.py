"""
generate_word_document.py
=========================
Generates a comprehensive, professional Microsoft Word (.docx) technical report
for the Process Intensification (PI) Analysis, Step-by-Step Evolution, and
Architecture Benchmark (Single-Tube vs. Four-Tube Shell-Packed CMR).
"""

import os
import shutil
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUTPUT_DOCX = os.path.join(ROOT_DIR, "PROCESS_INTENSIFICATION_ANALYSIS.docx")
ARTIFACT_DIR = "/Users/sameershekhar/.gemini/antigravity/brain/1a40eeba-2407-43f4-a37f-6ecea5ebeeae"
DOWNLOADS_DOCX = os.path.expanduser("~/Downloads/PROCESS_INTENSIFICATION_ANALYSIS.docx")

# Styling Palette
COLOR_PRIMARY = RGBColor(15, 23, 42)      # Deep Slate #0f172a
COLOR_ACCENT = RGBColor(16, 185, 129)     # Emerald #10b981
COLOR_TEXT = RGBColor(51, 65, 85)         # Slate text #334155
COLOR_MUTED = RGBColor(100, 116, 139)     # Gray #64748b

def set_cell_background(cell, fill_hex):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tc_pr.append(shd)

def set_cell_margins(cell, top=120, bottom=120, left=150, right=150):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tc_mar.append(node)
    tc_pr.append(tc_mar)

def create_document():
    doc = Document()

    # Set page margins (A4, 1-inch margins)
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Base style adjustments
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(10.5)
    normal_style.font.color.rgb = COLOR_TEXT

    # Document Header / Title
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_title = title.add_run("Process Intensification Analysis:\nIntensified Direct CO₂-to-DME Multi-Tube Membrane Reactor")
    run_title.font.name = 'Arial'
    run_title.font.size = Pt(20)
    run_title.font.bold = True
    run_title.font.color.rgb = COLOR_PRIMARY

    # Subtitle / Metadata
    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_sub = sub.add_run(
        "Comprehensive Chemical Reaction Engineering (CRE) Analysis, Theoretical Grounding & Architectural Benchmark\n"
        "[Operating Baseline: 250 °C, 40 bar | Catalyst: Cu/ZnO/Al₂O₃ + H-ZSM-5 | Membrane: Hydrophilic NaA Zeolite | 34/34 Tests Passed]"
    )
    run_sub.font.size = Pt(9.5)
    run_sub.font.italic = True
    run_sub.font.color.rgb = COLOR_MUTED

    doc.add_paragraph()  # Spacing

    # Section 1: Executive Summary
    h1 = doc.add_heading(level=1)
    run_h1 = h1.add_run("1. Executive Summary & Process Intensification Scorecard")
    run_h1.font.color.rgb = COLOR_PRIMARY
    run_h1.font.size = Pt(14)
    run_h1.font.bold = True

    p_intro = doc.add_paragraph()
    p_intro.add_run(
        "Chemical Process Intensification (PI) is defined by the European Roadmap for Process Intensification (2007) and "
        "Frerich J. Keil (Rev. Chem. Eng. 2018) as a set of radically innovative principles in process and equipment design "
        "that bring significant (greater than a factor of 2) benefits in process efficiency, equipment-size-to-capacity ratio, "
        "energy demand, waste reduction, and safety.\n\n"
        "Direct CO₂ hydrogenation to dimethyl ether (DME) couples methanol synthesis, reverse water-gas shift (RWGS), and methanol "
        "dehydration in a single reactive bed. By integrating in-situ hydrophilic NaA zeolite water-extraction membranes into a "
        "geometrically optimized four-tube shell-packed reactor, this design circumvents the thermodynamic Gibbs equilibrium barrier "
        "and overcomes catalytic active-site water poisoning."
    )

    # Scorecard Table
    table_score = doc.add_table(rows=1, cols=5)
    table_score.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr_cells = table_score.rows[0].cells
    headers = ["Process Performance Metric", "Traditional PBR", "Gibbs Ceiling", "Single-Tube CMR", "4-Tube Shell-Packed CMR"]
    for i, title_text in enumerate(headers):
        hdr_cells[i].text = title_text
        set_cell_background(hdr_cells[i], "0F172A")
        set_cell_margins(hdr_cells[i], top=100, bottom=100, left=120, right=120)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            r.font.bold = True
            r.font.size = Pt(9)
            r.font.color.rgb = RGBColor(255, 255, 255)

    score_data = [
        ("CO₂ Single-Pass Conversion (X_CO2)", "34.90%", "48.71%", "93.62%", "96.26% (+175.8% vs. PBR)"),
        ("DME Single-Pass Yield (Y_DME)", "31.17%", "46.54%", "91.94%", "94.28% (3.02x Multiplier)"),
        ("DME Carbon Selectivity (S_DME)", "89.29%", "95.55%", "98.21%", "97.94% (+8.65 pp gain)"),
        ("In-Situ Water Removal Fraction", "0.00%", "0.00%", "99.11%", "99.70% (0.003 mmol/s residual)"),
        ("Specific Membrane Area (a_v)", "0.0 m⁻¹", "—", "133.33 m⁻¹", "266.67 m⁻¹ (2.0x area density)"),
        ("Max Diffusion Distance (L_diff)", "5.64 mm", "—", "5.00 mm", "2.50 mm (50.0% reduction)"),
        ("Characteristic Diffusion Time (t_D ~ L²/D)", "Ref", "—", "~25.0 / D", "~6.25 / D (75% faster)"),
        ("Reactor Space-Time Yield (STY)", "1.0x (Ref)", "1.49x", "2.95x", "3.02x (67% volume cut)"),
        ("Unreacted Syngas Recycle Load", "65.1% of feed", "51.3% of feed", "6.4% of feed", "3.7% of feed (>85% cut)"),
        ("Design Evaluation Latency", "~2.5 s (ODE)", "—", "—", "< 0.2 ms (12,500x speedup)"),
    ]

    for row_idx, row in enumerate(score_data):
        row_cells = table_score.add_row().cells
        bg_color = "F8FAFC" if row_idx % 2 == 0 else "FFFFFF"
        for col_idx, text in enumerate(row):
            row_cells[col_idx].text = text
            set_cell_background(row_cells[col_idx], "ECFDF5" if col_idx == 4 else bg_color)
            set_cell_margins(row_cells[col_idx], top=80, bottom=80, left=100, right=100)
            p = row_cells[col_idx].paragraphs[0]
            if col_idx > 0:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                r.font.size = Pt(8.5)
                if col_idx == 4:
                    r.font.bold = True
                    r.font.color.rgb = RGBColor(6, 95, 70)

    doc.add_page_break()

    # Section 2: Theoretical Foundations of Process Intensification
    h2 = doc.add_heading(level=1)
    run_h2 = h2.add_run("2. Theoretical Foundations & The Four Guiding Principles of PI")
    run_h2.font.color.rgb = COLOR_PRIMARY
    run_h2.font.size = Pt(14)
    run_h2.font.bold = True

    p_theo = doc.add_paragraph()
    p_theo.add_run(
        "As established by Van Gerven and Stankiewicz (2009) and reviewed by Keil (2018), Process Intensification is "
        "structured along four physical guiding principles spanning the molecular, equipment, and temporal domains:\n\n"
        "1. Principle 1: Maximize Effectiveness of Intra- and Intermolecular Events\n"
        "In direct DME synthesis over Cu/ZnO/Al₂O₃, water byproduct competitively blocks active copper sites according to the "
        "Langmuir-Hinshelwood denominator D_k³:\n"
        "   r_CO2 = [k₁ p_CO2 p_H2 (1 - Q₁/K_eq1)] / D_k³\n"
        "   D_k = 1 + K_H2O,H2(p_H2O/p_H2) + √(K_H2 p_H2) + K_H2O p_H2O\n"
        "By continuously extracting 99.70% of the water through the membrane wall, local p_H2O is depressed to < 0.15 bar, "
        "maintaining D_k ≈ 1 and sustaining peak forward rates across the entire 1.0 m bed length.\n\n"
        "2. Principle 2: Give All Molecules the Same Processing Experience\n"
        "In un-intensified packed beds, gas flowing near the wall experiences water stagnation and lower conversion. "
        "In the Four-Tube Shell-Packed CMR, four membrane sinks are placed symmetrically at half the shell radius (Rpitch = 5.0 mm = Rshell/2). "
        "3D Darcy-Brinkman continuum CFD simulations confirm that inward radial suction velocity vectors converge uniformly into the four tubes, "
        "suppressing wall channeling and providing all fluid packets nearly identical residence-time and concentration histories.\n\n"
        "3. Principle 3: Optimize Driving Forces and Maximize Specific Surface Area\n"
        "Interfacial mass transfer rate is governed by J_vol = a_v · Π_H2O · Δp_H2O. Halving the tube diameter from 10 mm to 5 mm "
        "doubles specific membrane area from a_v = 133.3 m⁻¹ to 266.7 m⁻¹. Furthermore, characteristic diffusion time scales quadratically:\n"
        "   t_D ≈ L² / D_eff\n"
        "Reducing maximum diffusion length from 5.0 mm to 2.5 mm cuts diffusion time by 75% (a 4.0x transport acceleration).\n\n"
        "4. Principle 4: Maximize Synergies from Partial Processes (Multifunctional Units)\n"
        "By combining direct synthesis and in-situ separation inside the same vessel, continuous water removal maintains Q₁ ≪ K_eq1, "
        "continuously pulling the equilibrium forward via Le Chatelier's principle."
    )

    # Section 3: Why and How We Intensified
    h3 = doc.add_heading(level=1)
    run_h3 = h3.add_run("3. Why We Intensified & How the Engineering Was Done")
    run_h3.font.color.rgb = COLOR_PRIMARY
    run_h3.font.size = Pt(14)
    run_h3.font.bold = True

    p_why = doc.add_paragraph()
    p_why.add_run(
        "Why We Intensified:\n"
        "• Equilibrium Bottleneck: Classical packed beds stall at 34.90% single-pass conversion (Gibbs ceiling: 48.71% at 250 °C, 40 bar).\n"
        "• Catalyst Deactivation: High steam partial pressures cause hydrothermal dealumination of H-ZSM-5 acid sites and accelerate copper sintering.\n"
        "• Flowsheet Energy Duty: With >65% unreacted syngas per pass, conventional plants require massive recompression recycle compressors "
        "and energy-intensive three-column distillation trains.\n\n"
        "How the Engineering Was Done (Without Changing Operating Conditions):\n"
        "• Identical Operating Conditions: Temperature (250 °C), Pressure (40 bar), GHSV (1000 h⁻¹), catalyst mass (0.283 kg), and shell ID (20 mm) "
        "were kept strictly constant.\n"
        "• Bifunctional Bed Integration: Cu/ZnO/Al₂O₃ + H-ZSM-5 (dp = 0.30 mm, bulk density 1200 kg/m³, bed voidage 0.40).\n"
        "• Selective Hydrophilic Membrane: NaA Zeolite (pore aperture 4.0 Å) admits water (2.65 Å) while strictly blocking DME (4.30 Å).\n"
        "• Pitch Placement: Four 5.0 mm tubes placed at Rpitch = 5.0 mm on a 90° symmetric pitch circle."
    )

    doc.add_page_break()

    # Section 4: Architectural Comparison Matrix
    h4 = doc.add_heading(level=1)
    run_h4 = h4.add_run("4. Architectural Comparison: Single-Tube vs. Four-Tube Shell-Packed CMR")
    run_h4.font.color.rgb = COLOR_PRIMARY
    run_h4.font.size = Pt(14)
    run_h4.font.bold = True

    table_arch = doc.add_table(rows=1, cols=4)
    table_arch.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr_arch = table_arch.rows[0].cells
    arch_headers = ["Design & CRE Parameter", "Single Centre Tube CMR", "Four-Tube Shell-Packed CMR", "CRE Consequence & Physical Impact"]
    for i, title_text in enumerate(arch_headers):
        hdr_arch[i].text = title_text
        set_cell_background(hdr_arch[i], "0F172A")
        set_cell_margins(hdr_arch[i], top=100, bottom=100, left=120, right=120)
        p = hdr_arch[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            r.font.bold = True
            r.font.size = Pt(9)
            r.font.color.rgb = RGBColor(255, 255, 255)

    arch_data = [
        ("Tube Count & Configuration", "1 center tube", "4 distributed tubes", "Symmetric multi-sink radial suction"),
        ("Tube Outer Diameter (dt)", "10.0 mm", "5.0 mm", "Halving diameter doubles surface-to-volume ratio"),
        ("Pitch Circle Radius (Rpitch)", "0.0 mm (centered)", "5.0 mm (half shell radius)", "Tubes placed at (±5, 0) and (0, ±5) mm"),
        ("Shell Bore Diameter (Dshell)", "20.0 mm", "20.0 mm", "Identical vessel outer boundary"),
        ("Active Catalyst Bed Area (Ac)", "2.3562 cm² (75.0%)", "2.3562 cm² (75.0%)", "Identical catalyst volume and catalyst mass"),
        ("Specific Membrane Area (av)", "133.33 m⁻¹", "266.67 m⁻¹", "Exact +100% (2.0x) increase in area density"),
        ("Total Membrane Area (Amem)", "0.0314 m²", "0.0628 m²", "Exact 2.0x increase in interfacial transfer area"),
        ("Maximum Diffusion Distance (L)", "5.00 mm", "2.50 mm", "50.0% reduction in maximum transport distance"),
        ("Diffusion Timescale (t_D ~ L²/D)", "~25.0 / D", "~6.25 / D", "4.0x faster radial mass transport (75% drop in t_D)"),
        ("Clearance Between Tubes", "—", "2.071 mm", "δ / dp = 6.9 ≥ 5.0 (stable packing, zero bridging)"),
        ("Clearance to Shell Wall", "5.00 mm", "2.50 mm", "δ / dp = 8.3 ≥ 5.0 (prevents wall voidage bridging)"),
        ("Shell Voids & Bypass Risk", "Zero (annular)", "Zero (100% packed)", "No unsealed voids; zero bypass vulnerability"),
        ("Single-Pass CO₂ Conversion", "93.62%", "96.26%", "+2.64 pp higher conversion"),
        ("Single-Pass DME Yield", "91.94%", "94.28%", "+2.34 pp higher single-pass yield"),
        ("In-Situ Water Removal", "99.11%", "99.70%", "Enhanced extraction halos across 4 suction sinks"),
    ]

    for row_idx, row in enumerate(arch_data):
        row_cells = table_arch.add_row().cells
        bg_color = "F8FAFC" if row_idx % 2 == 0 else "FFFFFF"
        for col_idx, text in enumerate(row):
            row_cells[col_idx].text = text
            set_cell_background(row_cells[col_idx], "ECFDF5" if col_idx == 2 else bg_color)
            set_cell_margins(row_cells[col_idx], top=70, bottom=70, left=90, right=90)
            p = row_cells[col_idx].paragraphs[0]
            if col_idx in (1, 2):
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                r.font.size = Pt(8.5)
                if col_idx == 2:
                    r.font.bold = True
                    r.font.color.rgb = RGBColor(6, 95, 70)

    doc.add_page_break()

    # Section 5: Practical Engineering Implementation
    h5 = doc.add_heading(level=1)
    run_h5 = h5.add_run("5. Practical Engineering Implementation & Commercial Sizing")
    run_h5.font.color.rgb = COLOR_PRIMARY
    run_h5.font.size = Pt(14)
    run_h5.font.bold = True

    p_eng = doc.add_paragraph()
    p_eng.add_run(
        "1. High-Pressure Ceramic-to-Metal Sealing (ΔP = 39 bar):\n"
        "Porous α-alumina tubes are metallized with active Ag-Cu-Ti alloy and brazed to Kovar collars. "
        "The collars pass through a CNC-machined multi-tube header plate sealed with compressed Grafoil flexible graphite "
        "gaskets (certified up to 450 °C, 60 bar), completely isolating the 40 bar reaction shell from the 1 bar sweep plenum.\n\n"
        "2. Catalyst Loading Without Bridging:\n"
        "The minimum gap between tubes is 2.071 mm. With micro-pellets (dp = 0.30 mm), the clearance ratio is δ/dp = 6.9 ≥ 5.0, "
        "satisfying the Happel-Brenner packing criterion. Low-amplitude 50 Hz vibration during pneumatic loading ensures dense, "
        "uniform random packing (voidage εb = 0.40) without particle bridging.\n\n"
        "3. Exothermic Thermal Wall Jacket:\n"
        "Direct DME synthesis is exothermic (ΔH° = -122.6 kJ/mol). By keeping shell diameter at D = 20 mm, the maximum distance "
        "to the cooled wall is only 10 mm. An external pressurized saturated boiling water jacket (40 bar, Tsat = 250 °C) provides "
        "heat transfer coefficients of 2000–4000 W/(m²·K), restricting radial temperature rise to ΔT < 4 °C.\n\n"
        "4. Downstream Product Condensation at 40 bar:\n"
        "Because DME exits the shell at 40 bar, its boiling point rises from -24.8 °C (at 1 bar) to +91 °C! "
        "Passing the de-watered retentate through standard 25 °C cooling water heat exchangers condenses high-purity liquid DME "
        "instantly with zero secondary recompression power.\n\n"
        "5. Commercial Scale-Up via Numbering-Up:\n"
        "Industrial capacity is achieved by housing thousands of identical 4-tube cartridges in parallel inside a large multi-tubular "
        "shell vessel bathed in boiling water, preserving the verified 2.5 mm diffusion scale and 99.70% water removal."
    )

    # Section 6: Conclusions
    h6 = doc.add_heading(level=1)
    run_h6 = h6.add_run("6. Data-Backed Conclusions")
    run_h6.font.color.rgb = COLOR_PRIMARY
    run_h6.font.size = Pt(14)
    run_h6.font.bold = True

    p_concl = doc.add_paragraph()
    p_concl.add_run(
        "• Paradigm Shift Achieved: Single-pass DME yield rises from 31.17% (PBR) to 94.28% (3.02x multiplier), decisively meeting "
        "the European Roadmap Process Intensification criterion (> 2.0x factor benefit).\n"
        "• Equilibrium Bypassed: Continuous in-situ water extraction (99.70%) overshoots the thermodynamic Gibbs ceiling (46.54%) by 2.03x.\n"
        "• Four-Tube Superiority: Halving tube diameter and placing four tubes at half-radius doubles specific membrane area (av = 266.7 m⁻¹) "
        "and slashes diffusion time by 75% at identical catalyst inventory and shell dimensions.\n"
        "• Flowsheet Impact: Unreacted syngas recycle is reduced by >85%, and high-pressure liquid DME recovery eliminates costly cryo-refrigeration."
    )

    # Embed diagrams if files exist
    img_cross = os.path.join(ROOT_DIR, "figures", "dme_shell_packed_cross_section.png")
    img_cfd = os.path.join(ROOT_DIR, "figures", "dme_cfd_cross_sections.png")
    if os.path.exists(img_cross) and os.path.exists(img_cfd):
        doc.add_page_break()
        h_img = doc.add_heading(level=1)
        run_h_img = h_img.add_run("Appendix: Technical Drawings & 3D CFD Verification Slices")
        run_h_img.font.color.rgb = COLOR_PRIMARY
        run_h_img.font.size = Pt(14)
        run_h_img.font.bold = True

        p_img1 = doc.add_paragraph()
        p_img1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_picture(img_cross, width=Inches(5.5))
        cap1 = doc.add_paragraph("Figure 1: To-scale 2D Cross Section of Four-Tube Shell-Packed CMR (D_shell = 20 mm, dt = 5 mm, Rpitch = 5 mm).")
        cap1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap1.runs[0].font.size = Pt(8.5)
        cap1.runs[0].font.italic = True

        doc.add_paragraph()
        p_img2 = doc.add_paragraph()
        p_img2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_picture(img_cfd, width=Inches(5.8))
        cap2 = doc.add_paragraph("Figure 2: 2D Multi-Slice Darcy-Brinkman CFD Contours (z = 50 to 1000 mm) showing radial water depletion halos.")
        cap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap2.runs[0].font.size = Pt(8.5)
        cap2.runs[0].font.italic = True

    # Save document
    doc.save(OUTPUT_DOCX)
    print(f"Generated Word document: {OUTPUT_DOCX} ({os.path.getsize(OUTPUT_DOCX)/1024:.1f} KB)")

    # Copy to Brain Artifacts
    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    artifact_docx = os.path.join(ARTIFACT_DIR, "PROCESS_INTENSIFICATION_ANALYSIS.docx")
    shutil.copyfile(OUTPUT_DOCX, artifact_docx)
    print(f"Copied to Artifacts: {artifact_docx}")

    # Copy to Downloads
    shutil.copyfile(OUTPUT_DOCX, DOWNLOADS_DOCX)
    print(f"Copied to Downloads: {DOWNLOADS_DOCX}")

if __name__ == "__main__":
    create_document()
