"""
E-Methanol Membrane Reactor Package.
Scientific Reaction Engineering, Membrane Transport, Full-Length Industrial Sizing, and Machine Learning Surrogate Suite.
"""
from src.emethanol.reactor import (
    MembraneReactor1D,
    ModelConfig,
    ReactorSimulationResult,
    simulate_reactor,
    ODENonConvergenceError,
)
from src.emethanol.design import (
    IndustrialReactorDesignResult,
    design_full_length_reactor,
)
from src.emethanol.kinetics import calculate_rates
from src.emethanol.membrane import calculate_membrane_flux
from src.emethanol.thermodynamics import (
    STOICHIOMETRIC_MATRIX,
    ELEMENT_MATRIX,
    get_equilibrium_constants,
    get_reaction_enthalpies,
)
from src.emethanol.properties import (
    SPECIES,
    SPECIES_IDX,
    MW,
    R_GAS,
    get_pure_cp,
    get_mixture_cp,
    get_gas_density,
    get_gas_viscosity,
)
from src.emethanol.validation import compute_elemental_balances, validate_simulation_physics

__version__ = "2.1.0"

__all__ = [
    "MembraneReactor1D",
    "ModelConfig",
    "ReactorSimulationResult",
    "simulate_reactor",
    "IndustrialReactorDesignResult",
    "design_full_length_reactor",
    "ODENonConvergenceError",
    "calculate_rates",
    "calculate_membrane_flux",
    "STOICHIOMETRIC_MATRIX",
    "ELEMENT_MATRIX",
    "get_equilibrium_constants",
    "get_reaction_enthalpies",
    "SPECIES",
    "SPECIES_IDX",
    "MW",
    "R_GAS",
    "get_pure_cp",
    "get_mixture_cp",
    "get_gas_density",
    "get_gas_viscosity",
    "compute_elemental_balances",
    "validate_simulation_physics",
]
