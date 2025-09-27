# Dataclass-Based Environment Validation

This document describes the new dataclass-based validation system implemented to simplify environment setup and checking in BELLHOP.

## Overview

The issue requested that we "consider using dataclasses to simplify things" and specifically noted that "there should probably be no need to manually check that an option is in the list of possible options." This has been fully implemented.

## What Changed

### Before: Manual Option Checking

Previously, environment validation required manual assertions like:

```python
assert env['soundspeed_interp'] in _Maps.interp_rev, 'Invalid interpolation type: '+str(env['soundspeed_interp'])
assert env['surface_interp'] == _Strings.curvilinear or env['surface_interp'] == _Strings.linear, 'Invalid interpolation type: '+str(env['surface_interp'])
```

### After: Automatic Dataclass Validation

Now validation is automatic and comprehensive:

```python
# This automatically validates all options
config = EnvironmentConfig(soundspeed_interp='invalid_option')
# Raises: ValueError: Invalid soundspeed_interp: invalid_option. Must be one of: ['default', 'hexahedral', 'linear', 'nlinear', 'pchip', 'quadrilateral', 'spline']
```

## New Features

### 1. EnvironmentConfig Dataclass

A new dataclass that provides automatic validation of all environment options:

```python
from bellhop.environment_dataclass import EnvironmentConfig

# Automatic validation on creation
config = EnvironmentConfig(
    depth=40,
    soundspeed=1540,
    soundspeed_interp='linear',
    grid='rectilinear',
    beam_type='gaussian-cartesian'
)
```

### 2. Enhanced create_env2d_with_dataclass()

New function that provides immediate validation:

```python
import bellhop as bh

# This validates options immediately
env = bh.create_env2d_with_dataclass(
    depth=40,
    soundspeed_interp='linear'  # Validated against known options
)
```

### 3. Improved check_env2d()

The existing `check_env2d()` function now uses dataclass validation for option checking while preserving all existing complex validation logic.

### 4. Specialized Validation Functions

New validation functions for specific use cases:

```python
# Validate transmission loss modes
bh.validate_transmission_loss_mode('coherent')  # OK
bh.validate_transmission_loss_mode('invalid')   # Raises ValueError

# Validate source types  
bh.validate_source_type('point')     # OK
bh.validate_source_type('invalid')   # Raises ValueError
```

## Validated Options

The dataclass automatically validates these option categories:

- **Interpolation types**: soundspeed_interp, depth_interp, surface_interp
- **Boundary conditions**: bottom_boundary_condition, surface_boundary_condition  
- **Grid types**: grid
- **Beam types**: beam_type
- **Attenuation units**: attenuation_units
- **Volume attenuation**: volume_attenuation
- **Transmission loss modes**: coherent, incoherent, semicoherent
- **Source types**: point, line, default

## Error Messages

### Before (cryptic)
```
AssertionError: Invalid interpolation type: bad_option
```

### After (helpful)
```
ValueError: Invalid soundspeed_interp: bad_option. Must be one of: ['default', 'hexahedral', 'linear', 'nlinear', 'pchip', 'quadrilateral', 'spline']
```

## Backward Compatibility

All existing code continues to work unchanged:

```python
# This still works exactly as before
env = bh.create_env2d(depth=40, soundspeed=1540)
env = bh.check_env2d(env)
```

## Usage Examples

### Basic Usage

```python
import bellhop as bh

# Method 1: Use new dataclass validation
env = bh.create_env2d_with_dataclass(
    depth=40,
    soundspeed=1540,
    soundspeed_interp='linear'
)

# Method 2: Use existing interface (now with enhanced validation)
env = bh.create_env2d(depth=40, soundspeed=1540)
env = bh.check_env2d(env)  # Now includes dataclass validation
```

### Advanced Usage

```python
from bellhop.environment_dataclass import EnvironmentConfig

# Direct dataclass usage
config = EnvironmentConfig(
    name='My Acoustic Model',
    frequency=1000,
    depth=100,
    soundspeed_interp='spline',
    grid='rectilinear',
    beam_type='gaussian-cartesian',
    volume_attenuation='thorp'
)

# Convert to dictionary for existing functions
env = config.to_dict()
```

### Error Handling

```python
try:
    env = bh.create_env2d_with_dataclass(soundspeed_interp='invalid_option')
except ValueError as e:
    print(f"Invalid option: {e}")
    # Shows all valid alternatives
```

## Benefits

1. **Eliminates manual option checking**: No more manual assertions needed
2. **Better error messages**: Users see all valid options immediately  
3. **Type safety**: Dataclass provides structure and validation
4. **Maintainability**: Centralized validation logic
5. **Extensibility**: New options automatically get validation
6. **Backward compatibility**: Existing code unchanged

## Testing

Comprehensive test suite with 27+ tests covering:

- All option validation scenarios
- Integration with existing functions
- Backward compatibility
- Error message quality
- Edge cases

Run tests with:
```bash
pytest tests/test_dataclass_validation.py -v
```

## Implementation Details

The implementation includes:

- `EnvironmentConfig` dataclass with field validation
- `_validate_options_with_dataclass()` for integration  
- Validation helper functions for specific option types
- Full backward compatibility layer
- Comprehensive error messages with valid alternatives

This fully addresses the original issue request to use dataclasses to eliminate manual option checking while maintaining all existing functionality.