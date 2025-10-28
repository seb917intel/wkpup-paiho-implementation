# WKPUP Simulation - Pai Ho's Implementation

Alternative implementation of WKPUP (Wake-up) SPICE simulation framework for I3C and GPIO circuits.

## Overview

This repository contains Pai Ho's implementation of the WKPUP simulation system. While it achieves similar goals to the main implementation, it uses a different architectural approach.

## Project Structure

```
wkpup2/
├── i3c/          # I3C circuit simulations
│   └── 1p1v/     # 1.1V voltage domain
└── gpio/         # GPIO circuit simulations
    └── 1p1v/     # 1.1V voltage domain
```

## Related Repositories

- Main Implementation: [wkpup-simulation](https://github.com/seb917intel/wkpup-simulation)

## Author

Implementation by: **Pai Ho**  
Repository maintained by: Sebastian Chin (seb917intel)

## Usage

```bash
# Navigate to voltage domain
cd i3c/1p1v/

# Run simulations
./runme.sh
```

## License

Internal Intel project - Not for external distribution

## Notes

This is an alternative implementation approach. For the primary implementation with automation framework, see the main wkpup-simulation repository.
