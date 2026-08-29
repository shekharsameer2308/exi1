import numpy as np
from scipy.integrate import solve_ivp
from typing import Tuple, Dict

class ODENonConvergenceError(Exception):
    """Custom exception raised when the ODE solver fails to converge."""
    pass

class MembraneReactor1D:
    """
    1D Plug Flow Membrane Reactor for E-Methanol Synthesis.
    Kinetics: Vanden Bussche & Froment (1996)
    """
    def __init__(self, length: float = 1.0, diameter: float = 0.02, 
                 rho_cat: float = 1100.0, void_frac: float = 0.4):
        # Explicit type validation to prevent silent hostile inputs
        if not all(isinstance(val, (int, float)) for val in [length, diameter, rho_cat, void_frac]):
            raise TypeError("All reactor physical parameters must be numeric (int or float).")
        if length <= 0 or diameter <= 0 or rho_cat <= 0:
            raise ValueError("Reactor geometry and density must be strictly positive.")
        if not (0 < void_frac < 1):
            raise ValueError("Void fraction must be between 0 and 1 exclusive.")

        self.L = float(length)
        self.D = float(diameter)
        self.A_cs = np.pi * (self.D ** 2) / 4.0
        self.rho_cat = float(rho_cat)
        self.eps = float(void_frac)
        self.R_gas = 8.314  # J/(mol*K), universal constant

    def vbf_kinetics(self, p: np.ndarray, T: float) -> Tuple[float, float]:
        """
        Calculates reaction rates [mol/(kg_cat*s)] for MeOH synthesis and RWGS.
        p: Array of partial pressures [bar] -> [CO2, H2, CO, MeOH, H2O]
        """
        # Hard boundary enforcement: Partial pressures cannot be negative or strictly zero.
        # This prevents math domain errors in square roots and divisions.
        p_CO2, p_H2, p_CO, p_MeOH, p_H2O = np.maximum(p, 1e-10)
        
        if T <= 0:
            raise ValueError("Absolute temperature (T) must be strictly positive (Kelvin).")
            
        RT = self.R_gas * T
        
        # Kinetic and adsorption constants
        k5a = 1.09e5 * np.exp(-87500.0 / RT)
        k1 = 1.22e10 * np.exp(-94765.0 / RT)
        K_H2O_KH2half = 6.62e-11 * np.exp(124119.0 / RT)
        K_H2half = 0.499 * np.exp(17197.0 / RT)
        K_H2O = 6.37e-9 * np.exp(113700.0 / RT)
        
        # Thermodynamic equilibrium constants
        Keq1 = 10.0 ** (3066.0 / T - 10.592)
        Keq3 = 10.0 ** (-2073.0 / T + 2.029)
        
        # Adsorption denominator (guaranteed > 1.0 due to positive constants and pressures)
        denom = (1.0 + K_H2O_KH2half * (p_H2O / np.sqrt(p_H2)) + 
                 K_H2half * np.sqrt(p_H2) + K_H2O * p_H2O)
        
        # Reaction rates
        r_meoh = k5a * 3453.38 * p_CO2 * p_H2 * (1 - (p_MeOH * p_H2O) / (Keq1 * p_CO2 * (p_H2**3))) / (denom**3)
        r_rwgs = k1 * p_CO2 * p_H2 * (1 - (p_CO * p_H2O) / (Keq3 * p_CO2 * p_H2)) / denom
        
        return float(r_meoh), float(r_rwgs)

    def simulate(self, T_in: float, P_in: float, flow_in: float, h2_co2_ratio: float, 
                 water_permeance: float = 1e-7) -> Dict[str, float]:
        """Solves the reactor ODEs and returns Yield and Conversion."""
        if flow_in <= 0 or P_in <= 0 or h2_co2_ratio <= 0:
            raise ValueError("Operational parameters (flow, pressure, ratio) must be strictly positive.")

        F_CO2_0 = flow_in / (1.0 + h2_co2_ratio)
        F_H2_0 = flow_in - F_CO2_0
        F0 = np.array([F_CO2_0, F_H2_0, 0.0, 0.0, 0.0])
        
        def odefunc(z: float, F: np.ndarray) -> np.ndarray:
            F = np.maximum(F, 1e-15)
            F_tot = np.sum(F)
            p_bar = (F / F_tot) * P_in
            
            r_meoh, r_rwgs = self.vbf_kinetics(p_bar, T_in)
            
            stoich = np.array([
                [-1, -3,  0,  1,  1],
                [-1, -1,  1,  0,  1]
            ])
            rates = np.array([r_meoh, r_rwgs])
            
            source = self.rho_cat * self.A_cs * (stoich.T @ rates)
            
            flux = np.zeros(5)
            flux[4] = water_permeance * (p_bar[4] * 1e5)
            
            perimeter = np.pi * self.D
            return source - perimeter * flux

        # BDF method chosen explicitly for stiff chemical kinetic ODEs
        sol = solve_ivp(odefunc, [0, self.L], F0, method='BDF', rtol=1e-6, atol=1e-9)
        
        # EXPLICIT ERROR HANDLING: Do not proceed if ODE solver failed
        if not sol.success:
            raise ODENonConvergenceError(f"ODE Solver failed to converge at z={sol.t[-1]:.4f}: {sol.message}")
        
        F_out = sol.y[:, -1]
        co2_conversion = (F0[0] - F_out[0]) / F0[0]
        meoh_yield = F_out[3] / F0[0]
        
        return {
            "co2_conversion": float(co2_conversion),
            "meoh_yield": float(meoh_yield)
        }
