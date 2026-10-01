"""Validate packaged aircraft data and inference for the OpenAP additions."""

from importlib.resources import files

import numpy as np
import polars as pl

from acropole import FuelEstimator

OPENAP_ADDITIONS = (
    "A19N",
    "A20N",
    "A21N",
    "A343",
    "A359",
    "A388",
    "B37M",
    "B38M",
    "B39M",
    "B3XM",
    "B744",
    "B748",
    "B752",
    "B763",
    "B772",
    "B773",
    "B77W",
    "B788",
    "B789",
    "C550",
    "E145",
    "GLF6",
)


def test_packaged_parameters_are_complete_and_unique() -> None:
    params = pl.read_csv(str(files("acropole").joinpath("data/aircraft_params.csv")))
    assert params["ACFT_ICAO_TYPE"].n_unique() == params.height
    required = (
        "FUEL_FLOW_TO",
        "SURFACE",
        "MAX_OPE_ALTI",
        "MAX_OPE_MACH_NUM",
        "MAX_TO_WEIGHT",
        "OPE_EMPTY_WEIGHT",
        "ACFT_SPAN",
        "ACFT_LENGTH",
        "ENGINE_NUM",
        "MAX_OPE_SPEED",
    )
    for field in required:
        assert params[field].null_count() == 0
        values = params[field].to_numpy()
        assert np.isfinite(values).all(), field
        assert (values > 0).all(), field
    assert (params["MAX_TO_WEIGHT"] > params["OPE_EMPTY_WEIGHT"]).all()
    added = params.filter(pl.col("ACFT_ICAO_TYPE").is_in(OPENAP_ADDITIONS))
    assert added.height == len(OPENAP_ADDITIONS)
    assert (added["TRAIN_ON"] == 0).all()
    assert added["PERCENTAGE"].is_null().all()
    assert added["CONF_IND"].is_null().all()


def test_openap_aircraft_inference_with_and_without_mass() -> None:
    estimator = FuelEstimator()
    all_params = pl.read_csv(
        str(files("acropole").joinpath("data/aircraft_params.csv"))
    )
    frames = []
    for code in OPENAP_ADDITIONS:
        params = all_params.filter(pl.col("ACFT_ICAO_TYPE") == code)
        mass = (params["MAX_TO_WEIGHT"][0] + params["OPE_EMPTY_WEIGHT"][0]) / 2
        frames.append(
            pl.DataFrame(
                {
                    "typecode": [code] * 3,
                    "groundspeed": [250.0, 300.0, 350.0],
                    "altitude": [10000.0, 15000.0, 20000.0],
                    "vertical_rate": [1500.0, 1000.0, 500.0],
                    "mass": [mass] * 3,
                }
            )
        )
    flight = pl.concat(frames)
    for input_frame in (flight, flight.drop("mass")):
        result = estimator.estimate(input_frame)
        assert isinstance(result, pl.DataFrame)
        assert result["typecode"].equals(input_frame["typecode"])
        assert result["fuel_flow"].is_finite().all()
        assert (result["fuel_flow"] > 0).all()
        for code in OPENAP_ADDITIONS:
            group = input_frame.filter(pl.col("typecode") == code)
            bound = estimator.for_aircraft(code)
            direct = bound.estimate(
                groundspeed=group["groundspeed"].to_numpy(),
                altitude=group["altitude"].to_numpy(),
                vertical_rate=group["vertical_rate"].to_numpy(),
                mass=group["mass"].to_numpy() if "mass" in group.columns else None,
            )
            expected = result.filter(pl.col("typecode") == code)["fuel_flow"].to_numpy()
            np.testing.assert_allclose(direct, expected)
