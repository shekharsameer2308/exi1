"""
Unit tests for full-length industrial reactor design and multi-tubular bundle sizing.
"""
import pytest
import numpy as np
from src.emethanol.design import design_full_length_reactor


def test_full_length_reactor_design_commercial_scale():
    """Verify that commercial 100 TPD full-length reactor sizing generates valid engineering outputs."""
    design = design_full_length_reactor(
        target_production_tpd=100.0,
        tube_length=6.0,
        tube_diameter=0.038,
        temperature=503.15,
        pressure=60.0,
        h2_co2_ratio=3.5,
        water_permeance=1.8e-7,
        single_tube_flow=0.040,
    )

    assert design.number_of_tubes > 50, f"Expected multi-tube bundle, got {design.number_of_tubes}"
    assert design.actual_production_tpd >= 100.0
    assert design.total_catalyst_mass_tonnes > 1.0
    assert design.total_membrane_area_m2 > 100.0
    assert design.cooling_duty_mw > 0.1
    assert design.shell_diameter_m > 0.5
    assert design.single_tube_result is not None
    assert design.single_tube_result.solver_success
    assert design.single_tube_result.co2_conversion > 0.05
    assert design.single_tube_result.meoh_yield > 0.03


def test_pilot_scale_full_length_design():
    """Verify pilot scale sizing for 1 TPD output with 3.0 m tube length."""
    design_pilot = design_full_length_reactor(
        target_production_tpd=1.0,
        tube_length=3.0,
        tube_diameter=0.025,
        temperature=493.15,
        pressure=50.0,
        h2_co2_ratio=3.0,
        single_tube_flow=0.020,
    )

    assert design_pilot.number_of_tubes >= 5
    assert design_pilot.actual_production_tpd >= 1.0
    assert design_pilot.total_catalyst_mass_tonnes > 0.01
    assert design_pilot.single_tube_result.solver_success
