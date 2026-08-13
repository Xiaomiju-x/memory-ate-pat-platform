# BY25Q40AL PAT Generator — Regional-Final Public Edition

This directory contains the clean-room public edition of the team's regional-final
BY25Q40AL SPI NOR Flash PAT generator. It implements the device transactions and the
team's parameterized memory-test algorithms without embedding or copying any
competition- or vendor-provided PAT files.

## Supported flows

- Standard, Dual, and Quad SPI program/read flows
- All-zero, checkerboard, walking-one, walking-zero, sliding-diagonal, and GALPAT
- Page-aligned program ranges with exact read/compare ranges
- Chip erase plus three-point blank-check sampling
- WEL/WIP sequencing, volatile QE handling for Quad flows, and EStar-subset validation
- GUI and headless batch generation

## Run

Python 3.10 or newer is sufficient; this edition uses only the standard library.

```bash
python by25q40al_pat_generator.py
python by25q40al_pat_generator.py --batch --bus SPI --mode mode_2 \
  --start 000003h --end 0001F1h --output output
python by25q40al_pat_generator.py --validate output/STANDARD_MEMORY_PROGRAM_READ.pat
python -m unittest discover -s tests -v
```

On Windows, `build_exe.bat` runs the public tests and packages the GUI with
PyInstaller. The generated executable does not bundle third-party competition assets.

## Public/private boundary

The competition-internal edition was calibrated and regression-tested in an authorized
environment against materials supplied for the event. Those materials, their hashes,
and template-copy paths are intentionally absent here. This public edition produces
files from code and validates its own syntax and transaction model.

Generated PAT files are engineering starting points, not a guarantee of compatibility
with every AdaptStar-E installation. Check timing sets, levels, pin maps, opcodes, and
the current device datasheet on your own authorized ATE setup before use.

See [Legal & IP](../../docs/legal-and-ip.md) for the repository-wide disclosure policy.
