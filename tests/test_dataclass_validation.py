"""
Test dataclass-based environment validation.

This module tests the new dataclass-based validation system for environment
configuration, ensuring that options are automatically validated without
manual checking.
"""

import pytest
import numpy as np
import bellhop as bh
from bellhop.environment import Environment
from bellhop.constants import _Strings


class TestEnvironmentValidation:
    """Test the Environment dataclass validation."""

    def test_valid_default_config(self):
        """Test that default configuration is valid."""
        config = Environment()
        assert config.name == 'bellhop/python default'
        assert config.dimension == '2D'
        assert config.frequency == 25000.0

    def test_invalid_soundspeed_interp(self):
        """Test that invalid soundspeed interpolation raises ValueError."""
        with pytest.raises(ValueError, match="Invalid value for 'soundspeed_interp'"):
            Environment(soundspeed_interp='invalid_interpolation')

    def test_valid_soundspeed_interp_options(self):
        """Test that all valid soundspeed interpolation options work."""
        valid_options = ['spline', 'linear', 'quadrilateral', 'pchip', 'hexahedral', 'nlinear', 'default']
        for option in valid_options:
            config = Environment(soundspeed_interp=option)
            assert config.soundspeed_interp == option

    def test_invalid_depth_interp(self):
        """Test that invalid depth interpolation raises ValueError."""
        with pytest.raises(ValueError, match="Invalid value for 'depth_interp'"):
            Environment(depth_interp='invalid_interpolation')

    def test_valid_depth_interp_options(self):
        """Test that all valid depth interpolation options work."""
        valid_options = ['linear', 'curvilinear']
        for option in valid_options:
            config = Environment(depth_interp=option)
            assert config.depth_interp == option

    def test_invalid_surface_interp(self):
        """Test that invalid surface interpolation raises ValueError."""
        with pytest.raises(ValueError, match="Invalid value for 'surface_interp'"):
            Environment(surface_interp='invalid_interpolation')

    def test_invalid_bottom_boundary_condition(self):
        """Test that invalid bottom boundary condition raises ValueError."""
        with pytest.raises(ValueError, match="Invalid value for 'bottom_boundary_condition'"):
            Environment(bottom_boundary_condition='invalid_boundary')

    def test_invalid_surface_boundary_condition(self):
        """Test that invalid surface boundary condition raises ValueError."""
        with pytest.raises(ValueError, match="Invalid value for 'surface_boundary_condition'"):
            Environment(surface_boundary_condition='invalid_boundary')

    def test_valid_boundary_condition_options(self):
        """Test that all valid boundary condition options work."""
        valid_options = ['vacuum', 'acousto-elastic', 'rigid', 'from-file', 'default']
        for option in valid_options:
            config = Environment(bottom_boundary_condition=option)
            assert config.bottom_boundary_condition == option

    def test_valid_surface_boundary_condition_options(self):
        """Test that all valid boundary condition options work."""
        valid_options = ['vacuum', 'acousto-elastic', 'rigid', 'from-file', 'default']
        for option in valid_options:
            config = Environment(surface_boundary_condition=option)
            assert config.surface_boundary_condition == option

    def test_invalid_grid_type(self):
        """Test that invalid grid type raises ValueError."""
        with pytest.raises(ValueError, match="Invalid value for 'grid_type'"):
            Environment(grid_type='invalid_grid')

    def test_valid_grid_options(self):
        """Test that all valid grid options work."""
        valid_options = ['rectilinear', 'irregular', 'default']
        for option in valid_options:
            config = Environment(grid_type=option)
            assert config.grid_type == option

    def test_invalid_beam_type(self):
        """Test that invalid beam type raises ValueError."""
        with pytest.raises(ValueError, match="Invalid value for 'beam_type'"):
            Environment(beam_type='invalid_beam')

    def test_valid_beam_type_options(self):
        """Test that all valid beam type options work."""
        valid_options = ['hat-cartesian', 'hat-ray', 'gaussian-cartesian', 'gaussian-ray', 'default']
        for option in valid_options:
            config = Environment(beam_type=option)
            assert config.beam_type == option

    def test_invalid_attenuation_units(self):
        """Test that invalid attenuation units raise ValueError."""
        with pytest.raises(ValueError, match="Invalid value for 'attenuation_units'"):
            Environment(attenuation_units='invalid_units')

    def test_valid_attenuation_units_options(self):
        """Test that all valid attenuation units options work."""
        valid_options = [
            'nepers per meter', 'frequency dependent', 'dB per meter', 'dB per wavelength',
            'quality factor', 'loss parameter', 'default'
        ]
        for option in valid_options:
            config = Environment(attenuation_units=option)
            assert config.attenuation_units == option

    def test_invalid_volume_attenuation(self):
        """Test that invalid volume attenuation raises ValueError."""
        with pytest.raises(ValueError, match="Invalid value for 'volume_attenuation'"):
            Environment(volume_attenuation='invalid_attenuation')

    def test_valid_volume_attenuation_options(self):
        """Test that all valid volume attenuation options work."""
        valid_options = ['thorp', 'francois-garrison', 'biological', 'none']
        for option in valid_options:
            config = Environment(volume_attenuation=option)
            assert config.volume_attenuation == option


class TestDataclassIntegration:
    """Test integration of dataclass validation with existing functions."""

    def test_create_env_with_validation(self):
        """Test that create_env works with valid options and validation."""
        env = bh.create_env(
            depth=40,
            soundspeed=1540,
            soundspeed_interp='linear'
        )
        assert isinstance(env, Environment)
        assert env['depth'] == 40
        assert env['soundspeed'] == 1540
        assert env['soundspeed_interp'] == 'linear'

    def test_create_env_with_invalid_options(self):
        """Test that create_env fails with invalid options."""
        with pytest.raises(ValueError, match="Invalid value for 'soundspeed_interp'"):
            bh.create_env(soundspeed_interp='invalid_option')

    def test_backward_compatibility_preserved(self):
        """Test that existing dictionary-based interface still works."""
        # This should work exactly as before
        env = bh.create_env(depth=40, soundspeed=1540)
        env = bh.check_env(env)
        assert env['depth'] == 40
        assert env['soundspeed'].iloc[0,0] == 1540


class TestDataclassUtilities:
    """Test utility functions for dataclass conversion."""

    def test_to_dict_conversion(self):
        """Test conversion of dataclass to dictionary."""
        config = Environment(depth=40, soundspeed=1540)
        env_dict = config.to_dict()

        assert isinstance(env_dict, dict)
        assert env_dict['depth'] == 40
        assert env_dict['soundspeed'] == 1540
        assert 'name' in env_dict
        assert 'dimension' in env_dict

