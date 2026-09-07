#
# Copyright 2026 Membrane-Reactor-SciML Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
Soft Sensor State Estimator Module.
Estimates real-time localized membrane fouling f_foul(z, t) and catalyst
deactivation state a(t) from axial temperature and pressure drop measurements.
"""

import numpy as np


class MembraneReactorSoftSensor:
    """
    Observer / Extended State Estimator for Fouling & Catalyst Activity.
    """

    def __init__(self, baseline_permeance: float = 2.5e-7):
        self.Q0 = baseline_permeance

    def estimate_fouling_and_activity(
        self,
        measured_outlet_meoh_fraction: float,
        measured_delta_p_bar: float,
        measured_peak_T_K: float,
        simulated_expected_meoh_fraction: float,
        simulated_expected_delta_p_bar: float,
        simulated_expected_peak_T_K: float,
    ) -> dict[str, float]:
        """
        Estimates membrane fouling factor f_foul in [0, 1] (0 = clean, 1 = blocked)
        and catalyst activity a(t) in [0, 1].
        """
        # Residual tracking
        dP_ratio = measured_delta_p_bar / max(simulated_expected_delta_p_bar, 1e-4)
        meoh_ratio = measured_outlet_meoh_fraction / max(
            simulated_expected_meoh_fraction, 1e-4
        )
        dT_excess = measured_peak_T_K - simulated_expected_peak_T_K

        # Localized membrane fouling increases boundary resistance
        f_foul = float(np.clip(1.0 - (meoh_ratio / max(dP_ratio, 0.5)), 0.0, 0.95))

        # Catalyst deactivation reduces intrinsic turnover frequency
        catalyst_activity = float(
            np.clip(meoh_ratio * np.exp(-dT_excess / 100.0), 0.1, 1.0)
        )

        return {
            "membrane_fouling_factor": f_foul,
            "catalyst_activity_factor": catalyst_activity,
            "effective_permeance_mol_m2_s_Pa": self.Q0 * (1.0 - f_foul),
            "health_status": (
                "HEALTHY"
                if f_foul < 0.20 and catalyst_activity > 0.85
                else "MAINTENANCE_REQUIRED"
            ),
        }
