"""Tests of the _energy_system module.

This file is part of project oemof (github.com/oemof/oemof). It's copyrighted
by the contributors recorded in the version control history of the file,
available from its original location oemof/tests/test_components.py

SPDX-License-Identifier: MIT
"""

import pandas as pd

from oemof.solph import EnergySystem


def test_add_periods():
    """test method _add_periods of energy system"""
    timeindex = pd.date_range(start="2012-01-01", periods=10000, freq="H")
    periods = [
        pd.date_range(start="2012-01-01", periods=8784, freq="H"),
        pd.date_range(start="2013-01-01", periods=1217, freq="H"),
    ]
    es = EnergySystem(
        timeindex=timeindex, periods=periods, infer_last_interval=True
    )
    assert len(es.periods) == 2
    assert es.periods[0].equals(
        pd.date_range(start="2012-01-01", periods=8784, freq="H")
    )
    assert es.periods[1].equals(
        pd.date_range(start="2013-01-01", periods=1217, freq="H")
    )


def test_extract_periods_years():
    """test method _extract_periods_years of energy system"""
    t_idx_1 = pd.date_range("1/1/2020", periods=3, freq="H").to_series()
    t_idx_2 = pd.date_range("1/1/2041", periods=3, freq="H").to_series()
    t_idx_3 = pd.date_range("1/1/2050", periods=3, freq="H").to_series()
    timeindex = pd.concat([t_idx_1, t_idx_2, t_idx_3]).index
    periods = [t_idx_1, t_idx_2, t_idx_3]
    es = EnergySystem(
        timeindex=timeindex,
        timeincrement=[1] * len(timeindex),
        infer_last_interval=False,
        periods=periods,
    )
    periods_years = [0, 21, 30]
    assert es.periods_years == periods_years
