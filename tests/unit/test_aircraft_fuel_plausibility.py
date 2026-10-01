"""Offline numerical sanity checks, not measured-flight accuracy validation.

Cruise references were generated with OpenAP 2.6.2, revision
a19a1cd559aa51c2ff385a71ee1884a53d866a33, using each CSV row's engine:

    FuelFlow(typecode, eng=engine, use_synonym=True).enroute(
        mass=mass_kg, tas=tas_kt, alt=35000, vs=0
    ) * 3600

https://openap.dev/fuel_emission.html describes the model and input units.
OpenAP shares Acropole-derived fuel calibration, so this is a comparison against
another estimation method, not independent flight measurements. Its drag polar
aliases are A19N/A21N -> A20N, B37M/B39M/B3XM -> B38M, B763 -> B752,
B773 -> B77W, and E145 -> E75L. Aircraft geometry and engines remain type-specific.

Masses are fixed halfway between the source OEW and MTOW, rather than computed
from the installed CSV, so a broken mass parameter cannot move the benchmark.
References are total aircraft kg/h, rounded to three decimals. No OpenAP install
or network access is needed to run these tests.
"""

import numpy as np
import polars as pl
import pytest

from acropole import FuelEstimator

# (typecode, mass kg, true airspeed kt, OpenAP total cruise fuel flow kg/h)
CRUISE_REFERENCES: tuple[tuple[str, float, float, float], ...] = (
    ("A19N", 59050.0, 450.0, 1431.526),
    ("A20N", 61650.0, 450.0, 1485.652),
    ("A21N", 73500.0, 450.0, 1785.202),
    ("A343", 203000.0, 450.0, 7381.939),
    ("A359", 211200.0, 450.0, 7161.475),
    ("A388", 418500.0, 450.0, 12863.494),
    ("B37M", 62500.0, 450.0, 2147.342),
    ("B38M", 63500.0, 450.0, 2170.162),
    ("B39M", 66500.0, 450.0, 2240.742),
    ("B3XM", 67500.0, 450.0, 2264.971),
    ("B744", 289600.0, 450.0, 12205.573),
    ("B748", 333900.0, 450.0, 11697.469),
    ("B752", 87000.0, 450.0, 4156.319),
    ("B763", 124350.0, 450.0, 5425.700),
    ("B772", 217500.0, 450.0, 10156.975),
    ("B773", 229900.0, 450.0, 10108.813),
    ("B77W", 259650.0, 450.0, 10445.247),
    ("B788", 173500.0, 450.0, 4721.433),
    ("B789", 191000.0, 450.0, 6416.326),
    ("C550", 5252.0, 340.0, 607.319),
    ("E145", 17055.0, 420.0, 812.273),
    ("GLF6", 34600.0, 480.0, 1470.619),
)

# Broad engineering sanity margins, not claimed prediction accuracy. The
# unknown-mass path has a wider allowance because its assumed mass is unspecified.
KNOWN_MASS_RELATIVE_TOLERANCE = 0.50
UNKNOWN_MASS_RELATIVE_TOLERANCE = 0.55


@pytest.fixture(scope="module")
def estimator() -> FuelEstimator:
    return FuelEstimator()


@pytest.mark.parametrize(
    ("typecode", "mass_kg", "tas_kt", "reference_kgh"),
    CRUISE_REFERENCES,
    ids=[case[0] for case in CRUISE_REFERENCES],
)
@pytest.mark.parametrize("with_mass", [True, False], ids=["known-mass", "unknown-mass"])
def test_cruise_fuel_flow_matches_openap_scale(
    estimator: FuelEstimator,
    typecode: str,
    mass_kg: float,
    tas_kt: float,
    reference_kgh: float,
    with_mass: bool,
) -> None:
    # Steady, wind-free cruise: airspeed equals groundspeed; no acceleration.
    flight = pl.DataFrame(
        {
            "typecode": [typecode] * 3,
            "groundspeed": [tas_kt] * 3,
            "airspeed": [tas_kt] * 3,
            "altitude": [35000.0] * 3,
            "vertical_rate": [0.0] * 3,
        }
    )
    if with_mass:
        flight = flight.with_columns(pl.lit(mass_kg).alias("mass"))
    result = estimator.estimate(flight)
    assert isinstance(result, pl.DataFrame)
    tolerance = (
        KNOWN_MASS_RELATIVE_TOLERANCE if with_mass else UNKNOWN_MASS_RELATIVE_TOLERANCE
    )
    # Both public units must match the same physical reference, catching kg/s
    # versus kg/h mistakes as well as major per-engine/whole-aircraft scaling bugs.
    np.testing.assert_allclose(
        result["fuel_flow_kgh"].to_numpy(),
        reference_kgh,
        rtol=tolerance,
        atol=0,
        err_msg=f"{typecode} cruise fuel flow (total kg/h)",
    )
    np.testing.assert_allclose(
        result["fuel_flow"].to_numpy(),
        reference_kgh / 3600,
        rtol=tolerance,
        atol=0,
        err_msg=f"{typecode} cruise fuel flow (total kg/s)",
    )


@pytest.mark.parametrize(
    ("typecode", "mass_kg", "tas_kt", "reference_kgh"),
    CRUISE_REFERENCES,
    ids=[case[0] for case in CRUISE_REFERENCES],
)
def test_climb_level_descent_fuel_flow_ordering(
    estimator: FuelEstimator,
    typecode: str,
    mass_kg: float,
    tas_kt: float,
    reference_kgh: float,
) -> None:
    # Independent steady states at the same mass, speed and altitude. No second
    # column: these are not successive trajectory points implying acceleration.
    values = estimator.for_aircraft(typecode).estimate(
        groundspeed=np.full(3, tas_kt - 50),
        airspeed=np.full(3, tas_kt - 50),
        altitude=np.full(3, 20000.0),
        vertical_rate=np.array([1500.0, 0.0, -1500.0]),
        mass=np.full(3, mass_kg),
    )
    climb, level, descent = values
    assert np.isfinite(values).all(), typecode
    assert climb > level > descent > 0, (
        f"{typecode}: expected climb > level > descent, got {values * 3600} kg/h"
    )
