import math

SPEED_OF_LIGHT = 3e8  # metres per second


def dbm_to_watts(dbm: float) -> float:
    """Convert a power level in dBm to watts."""
    return 10 ** (dbm / 10) / 1000


def wavelength_m(freq_hz: float) -> float:
    """Return the wavelength in metres for a frequency given in hertz."""
    if freq_hz <= 0:
        raise ValueError("Frequency must be greater than zero.")
    return SPEED_OF_LIGHT / freq_hz


def free_space_path_loss_db(distance_km: float, freq_mhz: float) -> float:
    """Return free-space path loss in dB for a distance in km and a frequency in MHz."""
    if distance_km <= 0 or freq_mhz <= 0:
        raise ValueError("Distance and frequency must be greater than zero.")
    return 20 * math.log10(distance_km) + 20 * math.log10(freq_mhz) + 32.44


if __name__ == "__main__":
    print(dbm_to_watts(30))                      # expect 1.0
    print(wavelength_m(2.4e9))                   # expect about 0.125
    print(free_space_path_loss_db(1, 2400))      # expect about 100.04