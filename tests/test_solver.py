import pytest
import numpy as np
from core.solver_2d import ReactorConfig, AnnularReactor2DSolver

def test_cfd_reproduction():
    cfg_tr = ReactorConfig(is_membrane=False)
    res_tr = AnnularReactor2DSolver(cfg_tr).solve()
    
    cfg_mr = ReactorConfig(is_membrane=True)
    res_mr = AnnularReactor2DSolver(cfg_mr).solve()
    
    assert res_mr.co2_conversion_pct > res_tr.co2_conversion_pct
    assert res_mr.meoh_yield_pct > res_tr.meoh_yield_pct
    assert res_mr.retentate_exit_p_h2o_bar > 1.0
    assert res_mr.carbon_balance_error < 0.05
