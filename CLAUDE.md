# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
uv run ./codegen.sh                  # Regenerate SiLA2 boilerplate from feature XML files
uv run python -m unittest            # Run all tests
uv run python -m unittest tests.test_teleshake1536.TestTeleshake1536.test_GetRPM  # Run a single test
uv run python -m sila2_driver.thermoscientific.teleshake1536 --port 50050  # Start the SiLA2 server
```

Code style: Black and isort, both with `line-length = 120`.

## Architecture

This is a SiLA2 driver for the Thermo Scientific Teleshaker 1536. Documentation on the 
python implementation of the sila framework can be found at https://sila2.gitlab.io/sila_python/ .
The development workflow is:

**Edit XML → Run codegen → Implement base classes → Done**

```
feature_xml/*.sila.xml
    ↓  ./codegen.sh
src/sila2_driver/thermoscientific/teleshake1536/
├── generated/              # AUTO-GENERATED — never edit directly
├── feature_implementations/  # Hand-written business logic
├── api/                    # Low-level serial hardware interface
├── server.py               # SilaServer setup and feature registration
└── __main__.py             # CLI entry point (typer)
```

**`generated/`** contains base classes, client code, types, and error classes — one subdirectory per feature. Regenerate with `codegen.sh` whenever XML changes.

**`feature_implementations/`** contains subclasses of the generated base classes. Each implementation receives a `Teleshake1536` instance (or simulation object) and calls into `api/` for actual hardware communication.

**`api/`** handles serial communication: `frame.py` defines the 6-byte wire format (Ctrl, Cmd, Data2, Data1, Data0, CRC), `teleshake.py` exposes high-level commands (`SetRPM`, `StartDevice`, etc.), and `rpm_converter.py` maps RPM values to cycle times via a lookup table.

**Simulation mode** is controlled by `SimulationControllerImpl` — when active, `ShakeControllerImpl` uses a dummy serial object instead of a real device, which is also how tests work.



## SiLA2 Feature XML

Feature XML files must conform to the schema at:
`https://gitlab.com/SiLA2/sila_base/raw/master/schema/FeatureDefinition.xsd`

Valid `<DataType>` children are: `<Basic>`, `<List>`, `<Structure>`, `<Constrained>`, `<DataTypeIdentifier>`. There is no `<Optional>` type in the schema — do not invent elements. Always validate against the schema before running codegen.
