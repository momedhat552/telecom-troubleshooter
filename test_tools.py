import pytest
from tools import dbm_to_watts, wavelength_m, free_space_path_loss_db


def test_dbm_to_watts_30dbm_is_one_watt():
    assert dbm_to_watts(30) == pytest.approx(1.0)


def test_dbm_to_watts_0dbm_is_one_milliwatt():
    assert dbm_to_watts(0) == pytest.approx(0.001)


def test_wavelength_at_2_4_ghz():
    assert wavelength_m(2.4e9) == pytest.approx(0.125)


def test_free_space_path_loss_1km_at_2400_mhz():
    assert free_space_path_loss_db(1, 2400) == pytest.approx(100.04, abs=0.1)


def test_wavelength_zero_frequency_raises():
    with pytest.raises(ValueError):
        wavelength_m(0)


def test_path_loss_zero_distance_raises():
    with pytest.raises(ValueError):
        free_space_path_loss_db(0, 2400)