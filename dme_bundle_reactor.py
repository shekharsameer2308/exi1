"""
dme_bundle_reactor.py
=====================
Layout helpers and geometric modeling for multi-tube membrane reactor bundles.
Supports the four-tube bundle with uniform-thickness catalyst sleeve, as well
as comparative benchmark configurations.

Layouts supported:
  1. "sleeve": Four membrane tubes wrapped in uniform catalyst sleeves touching
     each other and the shell wall in tangent square packing.
  2. "centre_tube": Single membrane tube in the center of an annular catalyst bed.
  3. "concentric": Four concentric membrane cylinders with nested catalyst annulus.
  4. "shell": Four membrane tubes immersed in a catalyst-packed shell.
  5. "tubes": Catalyst packed inside the lumens of four membrane tubes.

References:
  - Richard et al. (2025), Int. J. Hydrogen Energy 112: 446-467
  - Yeassin et al. (2026), Chemical Engineering Journal / E-Fuel Reactor Architectures
"""

import numpy as np


def bundle_layout(
    catalyst="sleeve",
    d=None,
    Ac=None,
    t=None,
    L=1.0,
    rho_B=1200.0,
    dp=0.0003,  # 0.3 mm typical fine pellet diameter
    d1_centre=0.010,  # 10 mm default for single centre tube
):
    """
    Compute geometric parameters for membrane reactor layouts.

    Parameters:
      catalyst: str in {"sleeve", "centre_tube", "concentric", "shell", "tubes"}
      d: membrane tube outer diameter [m] (required for "sleeve", "shell")
      Ac: catalyst bed cross-sectional area [m^2] (optional if t given)
      t: catalyst sleeve thickness [m] (optional if Ac given)
      L: reactor length [m] (default 1.0 m)
      rho_B: catalyst bulk density [kg/m^3] (default 1200 kg/m^3)
      dp: catalyst particle diameter [m] (default 0.3 mm = 3e-4 m)
      d1_centre: membrane diameter for centre_tube layout [m]

    Returns:
      dict with complete geometry, areas, diameters, membrane area per volume,
      and practicality checks.
    """
    if catalyst == "sleeve":
        if d is None:
            raise ValueError("Membrane tube diameter 'd' must be specified for sleeve layout.")

        # Solve for t from Ac or Ac from t
        if t is None:
            if Ac is None:
                Ac = 1.0e-4  # Default 1 cm^2 (0.12 kg at 1200 kg/m^3, L=1m)
            # Ac = 4 * pi * t * (d + t) => 4*pi*t^2 + 4*pi*d*t - Ac = 0
            # t = (-d + sqrt(d^2 + Ac/pi)) / 2
            disc = d ** 2 + Ac / np.pi
            t = (-d + np.sqrt(disc)) / 2.0
        else:
            Ac = 4.0 * np.pi * t * (d + t)

        d_s = d + 2.0 * t  # Sleeve outer diameter
        # Four touching sleeves enclosed in tangent circle
        # Shell diameter D = (1 + sqrt(2)) * d_s
        D_shell = (1.0 + np.sqrt(2.0)) * d_s

        # Membrane perimeter per metre of bed length: 4 tubes of outer diameter d
        Pm = 4.0 * np.pi * d

        # Membrane area per bed volume [m^-1]
        # a_v = Pm / Ac = (4*pi*d) / (4*pi*t*(d+t)) = d / (t * (d + t))
        a_v = d / (t * (d + t))

        # Cross-sectional areas
        A_shell = (np.pi / 4.0) * (D_shell ** 2)
        A_sleeves_outer = np.pi * (d_s ** 2)  # 4 * (pi * d_s^2 / 4)
        A_tubes_inner = np.pi * (d ** 2)      # 4 * (pi * d^2 / 4)

        # Catalyst bed area Ac = A_sleeves_outer - A_tubes_inner
        # Total void space inside shell outside catalyst sleeves
        A_void_total = A_shell - A_sleeves_outer
        void_fraction_shell = A_void_total / A_shell

        # Central void pocket (between the 4 touching circles of diameter d_s)
        # Center square side = d_s, area = d_s^2; minus 4 quarter-circles = pi/4 * d_s^2
        A_center_void = (1.0 - np.pi / 4.0) * (d_s ** 2)
        A_outer_voids = A_void_total - A_center_void

        # Practicality check: catalyst particle size dp must be at most about t/5
        ratio_t_dp = t / dp
        is_practical = ratio_t_dp >= 5.0
        warning = None
        if not is_practical:
            warning = (
                f"IMPRACTICAL: Sleeve thickness t = {t*1e3:.2f} mm is less than 5 * dp "
                f"({5*dp*1e3:.2f} mm). Ratio t/dp = {ratio_t_dp:.2f} < 5.0. "
                f"High risk of severe wall channeling, bypass, and bridging."
            )

        W_cat = rho_B * Ac * L
        A_mem_total = Pm * L

        return {
            "layout": "sleeve",
            "d": float(d),
            "t": float(t),
            "d_s": float(d_s),
            "D_shell": float(D_shell),
            "Ac": float(Ac),
            "Pm": float(Pm),
            "a_v": float(a_v),
            "L": float(L),
            "W_cat": float(W_cat),
            "A_mem_total": float(A_mem_total),
            "A_shell": float(A_shell),
            "A_void_total": float(A_void_total),
            "A_center_void": float(A_center_void),
            "A_outer_voids": float(A_outer_voids),
            "void_fraction_shell": float(void_fraction_shell),
            "dp": float(dp),
            "ratio_t_dp": float(ratio_t_dp),
            "is_practical": bool(is_practical),
            "warning": warning,
        }

    elif catalyst == "centre_tube":
        # One membrane tube in center of annular catalyst bed
        if Ac is None:
            Ac = 1.0e-4
        d1 = d1_centre
        Pm = np.pi * d1
        D_shell = np.sqrt(4.0 * Ac / np.pi + d1 ** 2)
        a_v = Pm / Ac
        W_cat = rho_B * Ac * L
        A_mem_total = Pm * L

        return {
            "layout": "centre_tube",
            "d": float(d1),
            "t": float((D_shell - d1) / 2.0),
            "D_shell": float(D_shell),
            "Ac": float(Ac),
            "Pm": float(Pm),
            "a_v": float(a_v),
            "L": float(L),
            "W_cat": float(W_cat),
            "A_mem_total": float(A_mem_total),
            "dp": float(dp),
            "is_practical": True,
            "warning": None,
        }

    elif catalyst == "concentric":
        # Four concentric membrane tubes with interleaved annular catalyst bed
        if Ac is None:
            Ac = 1.0e-4
        # 4 nested tubes with equal radii spacing
        radii = np.linspace(0.003, 0.015, 4)
        Pm = float(np.sum(2.0 * np.pi * radii))
        D_shell = float(2.0 * (radii[-1] + 0.002))
        a_v = Pm / Ac
        W_cat = rho_B * Ac * L
        A_mem_total = Pm * L

        return {
            "layout": "concentric",
            "d": float(radii[0] * 2.0),
            "D_shell": float(D_shell),
            "Ac": float(Ac),
            "Pm": float(Pm),
            "a_v": float(a_v),
            "L": float(L),
            "W_cat": float(W_cat),
            "A_mem_total": float(A_mem_total),
            "dp": float(dp),
            "is_practical": True,
            "warning": None,
        }

    elif catalyst == "shell":
        # 4 membrane tubes immersed in shell packed with catalyst
        if d is None:
            d = 0.006
        if Ac is None:
            Ac = 1.0e-4
        # Ac = (pi/4)*D_shell^2 - 4*(pi/4)*d^2 = (pi/4)*D_shell^2 - pi*d^2
        D_shell = np.sqrt((4.0 / np.pi) * (Ac + np.pi * (d ** 2)))
        Pm = 4.0 * np.pi * d
        a_v = Pm / Ac
        W_cat = rho_B * Ac * L
        A_mem_total = Pm * L

        return {
            "layout": "shell",
            "d": float(d),
            "D_shell": float(D_shell),
            "Ac": float(Ac),
            "Pm": float(Pm),
            "a_v": float(a_v),
            "L": float(L),
            "W_cat": float(W_cat),
            "A_mem_total": float(A_mem_total),
            "dp": float(dp),
            "is_practical": True,
            "warning": None,
        }

    elif catalyst == "tubes":
        # Catalyst packed inside 4 tube lumens, permeate on shell side
        if Ac is None:
            Ac = 1.0e-4
        # Ac = 4 * (pi * d_in^2 / 4) = pi * d_in^2
        d_in = np.sqrt(Ac / np.pi)
        Pm = 4.0 * np.pi * d_in
        a_v = Pm / Ac  # 4 / d_in
        D_shell = (1.0 + np.sqrt(2.0)) * d_in * 1.2
        W_cat = rho_B * Ac * L
        A_mem_total = Pm * L

        return {
            "layout": "tubes",
            "d": float(d_in),
            "D_shell": float(D_shell),
            "Ac": float(Ac),
            "Pm": float(Pm),
            "a_v": float(a_v),
            "L": float(L),
            "W_cat": float(W_cat),
            "A_mem_total": float(A_mem_total),
            "dp": float(dp),
            "is_practical": True,
            "warning": None,
        }

    else:
        raise ValueError(f"Unknown catalyst layout: {catalyst}")
