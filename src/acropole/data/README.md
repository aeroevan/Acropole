# Aircraft parameter sources

The additional rows below were adapted from OpenAP by Junzi Sun and contributors
on 2026-09-30, at revision `a19a1cd559aa51c2ff385a71ee1884a53d866a33`. Existing aircraft parameters were retained.
OpenAP's data license is GPL-3.0; a copy is included in `OPENAP-DATA-LICENSE`.

Aircraft geometry, masses, engine count, maximum Mach, and ceiling come from the
linked aircraft YAML files. Masses are in kg, geometry in metres or square metres,
and ceilings are converted from metres to feet by dividing by 0.3048.
`MAX_OPE_SPEED` preserves Acropole's existing conversion: Mach multiplied by
575.0234616450498 knots (the speed of sound at the ISA tropopause).

Take-off fuel flow in kg/s per engine comes from the matching named engine in
[OpenAP's engine table](https://github.com/junzis/openap/blob/a19a1cd559aa51c2ff385a71ee1884a53d866a33/openap/data/engine/engines.csv).
The engine UID below identifies the exact record. The default engine is used except
for the four 737 MAX entries: their generic `LEAP-1B` is represented by the table's
`LEAP-1B28/28B2/28B1/28B3` record (UID `20CM101`, 1.075 kg/s per engine).
This is a representative family configuration, not a claim that every MAX variant
has the same engine rating. Supply custom parameters for a known configuration.

All added aircraft are turbofan jets (`TYPE=JET`, `ENGINE_TYPE=0`). Wake categories
use the conventional mass classes (L through 7,000 kg, M below 136,000 kg,
H from 136,000 kg), with A380 marked J.
`TRAIN_ON=0`; fleet engine percentage (`PERCENTAGE`) and model validation confidence
(`CONF_IND`) are unknown and left blank. These fields are not used in inference.

Each typecode uses one representative configuration. OpenAP's synonym mappings are
not imported: they can substitute unrelated aircraft and do not supply distinct
physical parameters. Adding parameters enables inference but does not establish
accuracy. In particular, A388's 845 m² wing area and GLF6's approximately 52,493 ft
ceiling exceed the model's normalization bounds (600 m² and 50,000 ft); predictions
for these values extrapolate beyond those bounds.

## Numerical sanity tests

The [fuel plausibility tests](../../../tests/unit/test_aircraft_fuel_plausibility.py)
cover every OpenAP addition, including B763. Offline cruise references were generated
with OpenAP 2.6.2 at the revision above, using the listed engine, 35,000 ft, zero
vertical rate, and a fixed mass halfway between source OEW and MTOW. Tests allow
50% relative difference with known mass and 55% when mass is unspecified; these
are broad sanity bounds, not accuracy targets. They check total kg/s and kg/h and
also require climb > level flight > descent at otherwise identical conditions.

OpenAP shares Acropole-derived fuel calibration and uses drag polar aliases for
some aircraft; the test module records those aliases and all comparison inputs.
These comparisons are not independent flight measurements. Larger differences
were observed in some climb/descent comparisons, especially for A388, so those
phases are checked for physical ordering rather than agreement with OpenAP.

## Aircraft source records

| Typecode | Aircraft | Aircraft source | Representative engine | Engine UID |
| --- | --- | --- | --- | --- |
| `A19N` | Airbus A319neo | [a19n.yml](https://github.com/junzis/openap/blob/a19a1cd559aa51c2ff385a71ee1884a53d866a33/openap/data/aircraft/a19n.yml) | PW1124G1-JM | `18PW118` |
| `A20N` | Airbus A320neo | [a20n.yml](https://github.com/junzis/openap/blob/a19a1cd559aa51c2ff385a71ee1884a53d866a33/openap/data/aircraft/a20n.yml) | PW1127G-JM | `18PW122` |
| `A21N` | Airbus A321neo | [a21n.yml](https://github.com/junzis/openap/blob/a19a1cd559aa51c2ff385a71ee1884a53d866a33/openap/data/aircraft/a21n.yml) | PW1133G-JM | `18PW126` |
| `A343` | Airbus A340-300 | [a343.yml](https://github.com/junzis/openap/blob/a19a1cd559aa51c2ff385a71ee1884a53d866a33/openap/data/aircraft/a343.yml) | CFM56-5C3 | `1CM011` |
| `A359` | Airbus A350-900 | [a359.yml](https://github.com/junzis/openap/blob/a19a1cd559aa51c2ff385a71ee1884a53d866a33/openap/data/aircraft/a359.yml) | Trent XWB-84 | `18RR079` |
| `A388` | Airbus A380-800 | [a388.yml](https://github.com/junzis/openap/blob/a19a1cd559aa51c2ff385a71ee1884a53d866a33/openap/data/aircraft/a388.yml) | GP7270 | `9EA001` |
| `B37M` | Boeing 737 MAX 7 | [b37m.yml](https://github.com/junzis/openap/blob/a19a1cd559aa51c2ff385a71ee1884a53d866a33/openap/data/aircraft/b37m.yml) | LEAP-1B28/28B2/28B1/28B3 | `20CM101` |
| `B38M` | Boeing 737 MAX 8 | [b38m.yml](https://github.com/junzis/openap/blob/a19a1cd559aa51c2ff385a71ee1884a53d866a33/openap/data/aircraft/b38m.yml) | LEAP-1B28/28B2/28B1/28B3 | `20CM101` |
| `B39M` | Boeing 737 MAX 9 | [b39m.yml](https://github.com/junzis/openap/blob/a19a1cd559aa51c2ff385a71ee1884a53d866a33/openap/data/aircraft/b39m.yml) | LEAP-1B28/28B2/28B1/28B3 | `20CM101` |
| `B3XM` | Boeing 737 MAX 10 | [b3xm.yml](https://github.com/junzis/openap/blob/a19a1cd559aa51c2ff385a71ee1884a53d866a33/openap/data/aircraft/b3xm.yml) | LEAP-1B28/28B2/28B1/28B3 | `20CM101` |
| `B744` | Boeing 747-400 | [b744.yml](https://github.com/junzis/openap/blob/a19a1cd559aa51c2ff385a71ee1884a53d866a33/openap/data/aircraft/b744.yml) | CF6-80C2B1F | `2GE045` |
| `B748` | Boeing 747-8 | [b748.yml](https://github.com/junzis/openap/blob/a19a1cd559aa51c2ff385a71ee1884a53d866a33/openap/data/aircraft/b748.yml) | GEnx-2B67 | `11GE139` |
| `B752` | Boeing 757-200 | [b752.yml](https://github.com/junzis/openap/blob/a19a1cd559aa51c2ff385a71ee1884a53d866a33/openap/data/aircraft/b752.yml) | RB211-535E4 | `5RR038` |
| `B763` | Boeing 767-300 | [b763.yml](https://github.com/junzis/openap/blob/a19a1cd559aa51c2ff385a71ee1884a53d866a33/openap/data/aircraft/b763.yml) | CF6-80C2B2 | `2GE042` |
| `B772` | Boeing 777-200/200ER | [b772.yml](https://github.com/junzis/openap/blob/a19a1cd559aa51c2ff385a71ee1884a53d866a33/openap/data/aircraft/b772.yml) | PW4090 | `10PW099` |
| `B773` | Boeing 777-300 | [b773.yml](https://github.com/junzis/openap/blob/a19a1cd559aa51c2ff385a71ee1884a53d866a33/openap/data/aircraft/b773.yml) | Trent 892 | `2RR027` |
| `B77W` | Boeing 777-300ER | [b77w.yml](https://github.com/junzis/openap/blob/a19a1cd559aa51c2ff385a71ee1884a53d866a33/openap/data/aircraft/b77w.yml) | GE90-115B | `21GE184` |
| `B788` | Boeing 787-8 | [b788.yml](https://github.com/junzis/openap/blob/a19a1cd559aa51c2ff385a71ee1884a53d866a33/openap/data/aircraft/b788.yml) | Trent 1000-E2 | `12RR064` |
| `B789` | Boeing 787-9 | [b789.yml](https://github.com/junzis/openap/blob/a19a1cd559aa51c2ff385a71ee1884a53d866a33/openap/data/aircraft/b789.yml) | Trent 1000-K2 | `12RR068` |
| `C550` | Cessna Citation II | [c550.yml](https://github.com/junzis/openap/blob/a19a1cd559aa51c2ff385a71ee1884a53d866a33/openap/data/aircraft/c550.yml) | JT15D-4 | `1PW036` |
| `E145` | Embraer ERJ145 (LR) | [e145.yml](https://github.com/junzis/openap/blob/a19a1cd559aa51c2ff385a71ee1884a53d866a33/openap/data/aircraft/e145.yml) | AE3007A1 | `6AL007` |
| `GLF6` | Gulfstream G650 / 650ER | [glf6.yml](https://github.com/junzis/openap/blob/a19a1cd559aa51c2ff385a71ee1884a53d866a33/openap/data/aircraft/glf6.yml) | BR700-725A1-12 | `11BR011` |
