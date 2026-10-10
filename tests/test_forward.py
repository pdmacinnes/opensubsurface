from dataclasses import replace
import numpy as np
import pytest

from opensubsurface.domain import Geometry
from opensubsurface.solvers import MeshSettings, PygimliForward, SimpegForward


MANIFEST = np.array([[0, 3, 1, 2], [3, 0, 1, 2], [1, 2, 0, 3]])


def test_simpeg_voltage_units_polarity_and_reciprocity():
    forward = SimpegForward(MeshSettings(1., 32.), MANIFEST)
    voltage, record = forward.solve()
    assert voltage[0] == pytest.approx(0.005305164769729845, rel=0.15)
    np.testing.assert_allclose(voltage, [voltage[0], -voltage[0], voltage[0]], atol=1e-12)
    assert record["maximum_relative_equation_residual"] < 1e-8
    assert record["observations"] == 3


def test_pygimli_reference_and_background_scaling():
    forward = PygimliForward(MeshSettings(3., 32.), MANIFEST)
    voltage, _ = forward.solve()
    np.testing.assert_allclose(voltage, [0.005305164769729845, -0.005305164769729845, 0.005305164769729845], rtol=1e-10, atol=1e-12)
    model = Geometry("H1", 3., 10.)
    first, _ = forward.solve(model)
    twin, _ = forward.solve(replace(model))
    np.testing.assert_allclose(twin, first, rtol=1e-10, atol=1e-12)
    scaled, _ = forward.solve(replace(model, background=80.))
    np.testing.assert_allclose(scaled, first * 0.8, rtol=1e-8, atol=1e-12)
