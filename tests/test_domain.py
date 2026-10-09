from dataclasses import replace
import numpy as np
import pytest

from opensubsurface.domain import (
    Geometry, candidate_manifest, canonical_configuration, discrimination,
    electrodes, homogeneous_voltage, manifest_bytes, noise_sigma,
    nuisance_bank, primary_catalog,
)


def test_known_halfspace_voltage_and_polarity():
    locations = np.array([[0., 0., 0.], [1., 0., 0.], [2., 0., 0.], [3., 0., 0.]])
    manifest = np.array([[0, 3, 1, 2], [3, 0, 1, 2], [1, 2, 0, 3]])
    actual = homogeneous_voltage(locations, manifest)
    np.testing.assert_allclose(actual, [0.015915494309189534, -0.015915494309189534, 0.015915494309189534])


def test_manifest_is_unique_canonical_and_reproducible():
    manifest = candidate_manifest()
    assert manifest.shape == (4096, 4)
    assert len(set(map(tuple, manifest))) == 4096
    assert all(len(set(row)) == 4 and tuple(row) == canonical_configuration(row) for row in manifest)
    assert manifest.min() == 0 and manifest.max() == 63
    assert manifest_bytes(manifest) == manifest_bytes(candidate_manifest())
    assert canonical_configuration([8, 2, 6, 1]) == (1, 6, 2, 8)


def test_geometry_catalog_and_matched_volumes():
    models, pairs = primary_catalog()
    assert len(models) == 30 and len(pairs) == 24
    assert sum(model.kind == "H1" for model in models.values()) == 6
    for pair in pairs:
        first, second = models[pair["h1"]], models[pair["h2"]]
        assert first.radius == 1.5
        assert second.radius == pytest.approx(1.1905507889761495)
        assert np.sum(second.radius ** 3 * np.ones(2)) == pytest.approx(first.radius ** 3)
        assert second.separation - 2 * second.radius > 0.618
        assert np.all(second.centers[:, 2] + second.radius < 0)
    assert Geometry("H1", 3, 10).identifier == Geometry("H1", 3., 10.).identifier


def test_bank_has_810_states_and_270_normalized_geometries():
    models, _ = primary_catalog()
    bank = {variant.identifier: variant for model in models.values() for variant in nuisance_bank(model)}
    assert len(bank) == 810
    assert len({replace(model, background=100.).identifier for model in bank.values()}) == 270


def test_nuisance_bank_and_material_twins():
    first = Geometry("H1", 3., 10.)
    bank = nuisance_bank(first)
    assert len(bank) == 27 and len({model.identifier for model in bank}) == 27
    assert {model.background for model in bank} == {80., 100., 125.}
    points = np.array([[0., 0., -3.], [3., 0., -3.], [0., 0., 0.]])
    np.testing.assert_array_equal(first.contains(points), [True, False, False])
    np.testing.assert_array_equal(first.contains(points), replace(first).contains(points))


def test_noise_floor_and_gaussian_diagnostic():
    sigma = noise_sigma(np.array([0., -0.001]), 0.01, 1e-6)
    np.testing.assert_allclose(sigma, [1e-6, 1.004987562112089e-5])
    distance, error, contributions = discrimination(np.array([0., 0.]), np.array([3., 4.]), np.ones(2))
    assert distance == 5.
    assert error == pytest.approx(0.006209665325776132)
    np.testing.assert_array_equal(contributions, [9., 16.])
    assert discrimination(np.zeros(2), np.zeros(2), np.ones(2))[:2] == (0., 0.5)


@pytest.mark.parametrize("kwargs", [dict(kind="H1", depth=1., contrast=10.), dict(kind="H2", depth=3., contrast=10., separation=2.), dict(kind="H1", depth=3., contrast=-1.)])
def test_invalid_physical_models_are_rejected(kwargs):
    with pytest.raises(ValueError):
        Geometry(**kwargs)


def test_invalid_survey_and_noise_are_rejected():
    with pytest.raises(ValueError):
        canonical_configuration([0, 1, 1, 3])
    with pytest.raises(ValueError):
        candidate_manifest(4, electrode_count=4)
    with pytest.raises(ValueError):
        noise_sigma(np.zeros(2), 0.01, 0.)
    assert electrodes().shape == (64, 3)
