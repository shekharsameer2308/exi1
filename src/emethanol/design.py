"""
Industrial and Pilot Scale Full-Length Reactor Design and Scale-Up Module.
Designs multi-tubular packed-bed membrane reactors for e-methanol synthesis.
"""
import numpy as np
from typing import Dict, Any, Tuple, Optional
from dataclasses import dataclass, field

from src.emethanol.reactor import simulate_reactor, ReactorSimulationResult, ModelConfig
from src.emethanol.properties import MW, R_GAS


@dataclass
class IndustrialReactorDesignResult:
    """Structured container for full-length industrial reactor sizing and economics."""
    # Scale & Target Specifications
    scale_name: str = "Commercial Industrial"
    target_production_tpd: float = 100.0  # Metric Tons Methanol per day (TPD)
    actual_production_tpd: float = 100.0
    
    # Reactor Geometry & Bundle Sizing
    tube_length_m: float = 6.0
    tube_inner_diameter_m: float = 0.038   # 38 mm (1.5 inch schedule 40)
    tube_outer_diameter_m: float = 0.042
    number_of_tubes: int = 1500
    shell_diameter_m: float = 2.2
    reactor_total_volume_m3: float = 10.2
    
    # Catalyst & Membrane Inventory
    single_tube_catalyst_kg: float = 7.48
    total_catalyst_mass_tonnes: float = 11.22
    single_tube_membrane_area_m2: float = 0.716
    total_membrane_area_m2: float = 1074.4
    membrane_area_to_volume_ratio: float = 105.3  # m^2 / m^3
    
    # Process Streams & Material Balance (TPD)
    co2_feed_tpd: float = 142.5
    h2_feed_tpd: float = 19.8
    total_feed_syngas_tpd: float = 162.3
    water_byproduct_total_tpd: float = 56.2
    water_extracted_membrane_tpd: float = 53.4
    co_byproduct_tpd: float = 3.2
    unreacted_syngas_tpd: float = 3.5
    
    # Energy, Cooling & Space Velocities
    cooling_duty_mw: float = 2.15
    electrolyzer_power_mw: float = 45.3   # Assuming 50 kWh/kg H2
    ghsv_h_inv: float = 3200.0            # Gas Hourly Space Velocity (h^-1)
    whsv_h_inv: float = 0.60              # Weight Hourly Space Velocity (h^-1)
    superficial_velocity_m_s: float = 0.45
    pressure_drop_bar: float = 1.25
    
    # Single-Tube Performance Profile
    single_tube_result: Optional[ReactorSimulationResult] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converts design metrics to structured dictionary."""
        return {
            "scale_name": self.scale_name,
            "target_production_tpd": self.target_production_tpd,
            "actual_production_tpd": self.actual_production_tpd,
            "tube_length_m": self.tube_length_m,
            "tube_inner_diameter_m": self.tube_inner_diameter_m,
            "number_of_tubes": self.number_of_tubes,
            "shell_diameter_m": self.shell_diameter_m,
            "total_catalyst_mass_tonnes": self.total_catalyst_mass_tonnes,
            "total_membrane_area_m2": self.total_membrane_area_m2,
            "membrane_area_to_volume_ratio": self.membrane_area_to_volume_ratio,
            "co2_feed_tpd": self.co2_feed_tpd,
            "h2_feed_tpd": self.h2_feed_tpd,
            "water_extracted_membrane_tpd": self.water_extracted_membrane_tpd,
            "cooling_duty_mw": self.cooling_duty_mw,
            "electrolyzer_power_mw": self.electrolyzer_power_mw,
            "ghsv_h_inv": self.ghsv_h_inv,
            "pressure_drop_bar": self.pressure_drop_bar,
        }


def design_full_length_reactor(
    target_production_tpd: float = 100.0,
    tube_length: float = 6.0,
    tube_diameter: float = 0.038,
    temperature: float = 503.15,          # 230 °C
    pressure: float = 60.0,               # 60 bar
    h2_co2_ratio: float = 3.5,
    water_permeance: float = 1.8e-7,
    single_tube_flow: float = 0.050,      # mol/s per tube
    catalyst_density: float = 1100.0,
    void_fraction: float = 0.40,
    particle_diameter: float = 0.003,     # 3 mm pellets
    tube_pitch_ratio: float = 1.35,       # Pitch-to-diameter ratio
    scale_name: str = "Commercial Industrial Multi-Tubular",
) -> IndustrialReactorDesignResult:
    """
    Simulates full-length single tube physics (L = 4.0 - 8.0 m) and calculates full multi-tubular bundle sizing.
    """
    # 1. Simulate Full-Length Single-Tube Physics
    res_tube = simulate_reactor(
        temperature=temperature,
        pressure=pressure,
        total_flow=single_tube_flow,
        h2_co2_ratio=h2_co2_ratio,
        water_permeance=water_permeance,
        reactor_length=tube_length,
        reactor_diameter=tube_diameter,
        membrane_enabled=True,
        non_isothermal=True,
        pressure_drop=True,
    )

    # 2. Single-Tube Mass Balances & Production
    # Methanol molar flow at outlet [mol/s]
    F_meoh_tube = res_tube.F_CH3OH[-1] + res_tube.cumulative_h2o_removed[-1]*0.0  # mol/s
    mw_meoh_kg = MW[3] * 1e-3  # 0.03204 kg/mol
    
    # Single tube production in Metric Tons/Day (TPD)
    tpd_per_tube = F_meoh_tube * mw_meoh_kg * 86400.0 * 1e-3  # tonnes/day

    # Number of tubes required to meet target production
    if tpd_per_tube > 1e-8:
        n_tubes = int(np.ceil(target_production_tpd / tpd_per_tube))
    else:
        n_tubes = 5000

    actual_tpd = n_tubes * tpd_per_tube

    # 3. Catalyst & Membrane Inventory
    A_cs_tube = np.pi * (tube_diameter ** 2) / 4.0
    V_bed_tube = A_cs_tube * tube_length
    cat_kg_tube = catalyst_density * V_bed_tube
    total_cat_tonnes = (n_tubes * cat_kg_tube) * 1e-3

    A_mem_tube = np.pi * tube_diameter * tube_length
    total_mem_m2 = n_tubes * A_mem_tube
    area_to_vol = total_mem_m2 / (n_tubes * V_bed_tube)

    # 4. Shell Sizing (Triangular Pitch Array)
    d_outer = tube_diameter + 0.004  # 4 mm wall thickness
    pitch = tube_pitch_ratio * d_outer
    bundle_area = n_tubes * (0.866 * (pitch ** 2))
    shell_diameter = float(np.sqrt(4.0 * bundle_area / np.pi) * 1.15)  # 15% clearance

    # 5. Plant Feedstock Consumption & Energy Duty
    F_CO2_tube_0 = single_tube_flow / (1.0 + h2_co2_ratio)
    F_H2_tube_0 = single_tube_flow - F_CO2_tube_0

    co2_feed_tpd = (n_tubes * F_CO2_tube_0 * MW[0] * 1e-3 * 86400.0) * 1e-3
    h2_feed_tpd = (n_tubes * F_H2_tube_0 * MW[1] * 1e-3 * 86400.0) * 1e-3
    total_feed_tpd = co2_feed_tpd + h2_feed_tpd

    # Total water extracted through membrane [TPD]
    F_h2o_perm_tube = res_tube.cumulative_h2o_removed[-1]
    water_extracted_tpd = (n_tubes * F_h2o_perm_tube * MW[4] * 1e-3 * 86400.0) * 1e-3

    # Total reaction heat / cooling duty [MW]
    # ΔH_rxn ~ 49.5 kJ/mol MeOH
    cooling_duty_mw = (n_tubes * F_meoh_tube * 52000.0) * 1e-6  # MW thermal

    # Electrolyzer Power Required (assuming 50 kWh / kg H2)
    h2_kg_day = h2_feed_tpd * 1000.0
    h2_kg_sec = h2_kg_day / 86400.0
    electrolyzer_mw = h2_kg_sec * 50.0 * 3.6  # MW electrical

    # Space Velocities
    # STP volume flow [Nm^3/h]
    V_stp_tube_m3_s = (single_tube_flow * 0.022414) # m^3(STP)/s
    ghsv = float((V_stp_tube_m3_s * 3600.0) / V_bed_tube)
    
    feed_mass_kg_h_tube = (F_CO2_tube_0 * MW[0] + F_H2_tube_0 * MW[1]) * 1e-3 * 3600.0
    whsv = float(feed_mass_kg_h_tube / cat_kg_tube)

    return IndustrialReactorDesignResult(
        scale_name=scale_name,
        target_production_tpd=target_production_tpd,
        actual_production_tpd=float(actual_tpd),
        tube_length_m=tube_length,
        tube_inner_diameter_m=tube_diameter,
        tube_outer_diameter_m=d_outer,
        number_of_tubes=n_tubes,
        shell_diameter_m=float(shell_diameter),
        reactor_total_volume_m3=float(n_tubes * V_bed_tube),
        single_tube_catalyst_kg=float(cat_kg_tube),
        total_catalyst_mass_tonnes=float(total_cat_tonnes),
        single_tube_membrane_area_m2=float(A_mem_tube),
        total_membrane_area_m2=float(total_mem_m2),
        membrane_area_to_volume_ratio=float(area_to_vol),
        co2_feed_tpd=float(co2_feed_tpd),
        h2_feed_tpd=float(h2_feed_tpd),
        total_feed_syngas_tpd=float(total_feed_tpd),
        water_extracted_membrane_tpd=float(water_extracted_tpd),
        cooling_duty_mw=float(cooling_duty_mw),
        electrolyzer_power_mw=float(electrolyzer_mw),
        ghsv_h_inv=float(ghsv),
        whsv_h_inv=float(whsv),
        pressure_drop_bar=float(res_tube.pressure_drop_bar),
        single_tube_result=res_tube,
    )
