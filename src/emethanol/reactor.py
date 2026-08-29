import numpy as np
from scipy.integrate import solve_ivp
from typing import Tuple, Dict

class MembraneReactor1D:
    """
    1D Plug Flow Membrane Reactor for E-Methanol Synthesis.
    Kinetics: Vanden Bussche & Froment (1996)
    """
    def __init__(self, length: float = 1.0, diameter: float = 0.02, 
                 rho_cat: float = 1100.0, void_frac: float = 0.4):
        self.L = length
        self.D = diameter
        self.A_cs = np.pi * (self.D ** 2) / 4.0
        self.rho_cat = rho_cat
        self.eps = void_frac
        self.R_gas = 8.314  # J/(mol*K)

    def vbf_kinetics(self, p: np.ndarray, T: float) -> Tuple[float, float]:
        """
        Calculates reaction rates [mol/(kg_cat*s)] for MeOH synthesis and RWGS.
        p: Array of partial pressures [bar] -> [CO2, H2, CO, MeOH, H2O]
        """
        p_CO2, p_H2, p_CO, p_MeOH, p_H2O = np.maximum(p, 1e-10) # Prevent div by zero
        RT = self.R_gas * T
        
        # Kinetic and adsorption constants (temperature dependent)
        k5a = 1.09e5 * np.exp(-87500.0 / RT)
        k1 = 1.22e10 * np.exp(-94765.0 / RT)
        K_H2O_KH2half = 6.62e-11 * np.exp(124119.0 / RT)
        K_H2half = 0.499 * np.exp(17197.0 / RT)
        K_H2O = 6.37e-9 * np.exp(113700.0 / RT)
        
        # Thermodynamic equilibrium constants
        Keq1 = 10.0 ** (3066.0 / T - 10.592) # CO2 + 3H2 <=> CH3OH + H2O
        Keq3 = 10.0 ** (-2073.0 / T + 2.029) # CO2 + H2 <=> CO + H2O
        
        denom = (1.0 + K_H2O_KH2half * (p_H2O / np.sqrt(p_H2)) + 
                 K_H2half * np.sqrt(p_H2) + K_H2O * p_H2O)
        
        # Rate of MeOH Synthesis (R1)
        r_meoh = k5a * 3453.38 * p_CO2 * p_H2 * (1 - (p_MeOH * p_H2O) / (Keq1 * p_CO2 * (p_H2**3))) / (denom**3)
        # Rate of RWGS (R2)
        r_rwgs = k1 * p_CO2 * p_H2 * (1 - (p_CO * p_H2O) / (Keq3 * p_CO2 * p_H2)) / denom
        
        return r_meoh, r_rwgs

    def simulate(self, T_in: float, P_in: float, flow_in: float, h2_co2_ratio: float, 
                 water_permeance: float = 1e-7) -> Dict[str, float]:
        """Solves the reactor ODEs and returns Yield and Conversion."""
        # Initial molar flows [mol/s]: CO2, H2, CO, MeOH, H2O
        F_CO2_0 = flow_in / (1.0 + h2_co2_ratio)
        F_H2_0 = flow_in - F_CO2_0
        F0 = np.array([F_CO2_0, F_H2_0, 0.0, 0.0, 0.0])
        
        def odefunc(z: float, F: np.ndarray) -> np.ndarray:
            F = np.maximum(F, 1e-15)
            F_tot = np.sum(F)
            p_bar = (F / F_tot) * P_in # Partial pressures [bar]
            
            r_meoh, r_rwgs = self.vbf_kinetics(p_bar, T_in)
            
            # Stoichiometry matrix [Reactions x Species]
            # R1: -1 CO2, -3 H2, +0 CO, +1 MeOH, +1 H2O
            # R2: -1 CO2, -1 H2, +1 CO, +0 MeOH, +1 H2O
            stoich = np.array([
                [-1, -3,  0,  1,  1],
                [-1, -1,  1,  0,  1]
            ])
            rates = np.array([r_meoh, r_rwgs])
            
            # Species source term: rho_cat * A_cs * sum(nu * r)
            source = self.rho_cat * self.A_cs * (stoich.T @ rates)
            
            # Membrane flux (selective water removal)
            # J = permeance * driving_force (simplified LDF)
            # Assuming sweep gas has 0 partial pressure of water
            flux = np.zeros(5)
            flux[4] = water_permeance * (p_bar[4] * 1e5) # Convert bar to Pa for permeance
            
            # Mass balance: dF/dz = source - Perimeter * flux
            perimeter = np.pi * self.D
            dFdz = source - perimeter * flux
            return dFdz

        # Solve ODE
        sol = solve_ivp(odefunc, [0, self.L], F0, method='BDF')
        
        F_out = sol.y[:, -1]
        co2_conversion = (F0[0] - F_out[0]) / F0[0]
        meoh_yield = F_out[3] / F0[0] # Moles MeOH out / Moles CO2 in
        
        return {
            "co2_conversion": float(co2_conversion),
            "meoh_yield": float(meoh_yield)
        }
