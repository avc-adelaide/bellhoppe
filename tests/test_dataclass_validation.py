"""
Test dataclass-based environment validation.

This module tests the new dataclass-based validation system for environment
configuration, ensuring that options are automatically validated without
manual checking.
"""

import pytest
import numpy as np
import bellhop as bh
from bellhop.environment import (
    EnvironmentConfig,
    _validate_transmission_loss_mode,
    _validate_source_type
)
from bellhop.constants import _Strings


class TestEnvironmentConfigValidation:
    """Test the EnvironmentConfig dataclass validation."""

    def test_valid_default_config(self):
        """Test that default configuration is valid."""
        config = EnvironmentConfig()
        assert config.name == 'bellhop/python default'
        assert config.type == '2D'
        assert config.frequency == 25000.0

    def test_invalid_soundspeed_interp(self):
        """Test that invalid soundspeed interpolation raises ValueError."""
        with pytest.raises(ValueError, match="Invalid soundspeed_interp"):
            EnvironmentConfig(soundspeed_interp='invalid_interpolation')

    def test_valid_soundspeed_interp_options(self):
        """Test that all valid soundspeed interpolation options work."""
        valid_options = ['spline', 'linear', 'quadrilateral', 'pchip', 'hexahedral', 'nlinear', 'default']
        for option in valid_options:
            config = EnvironmentConfig(soundspeed_interp=option)
            assert config.soundspeed_interp == option

    def test_invalid_depth_interp(self):
        """Test that invalid depth interpolation raises ValueError."""
        with pytest.raises(ValueError, match="Invalid depth_interp"):
            EnvironmentConfig(depth_interp='invalid_interpolation')

    def test_valid_depth_interp_options(self):
        """Test that all valid depth interpolation options work."""
        valid_options = ['linear', 'curvilinear']
        for option in valid_options:
            config = EnvironmentConfig(depth_interp=option)
            assert config.depth_interp == option

    def test_invalid_surface_interp(self):
        """Test that invalid surface interpolation raises ValueError."""
        with pytest.raises(ValueError, match="Invalid surface_interp"):
            EnvironmentConfig(surface_interp='invalid_interpolation')

    def test_invalid_bottom_boundary_condition(self):
        """Test that invalid bottom boundary condition raises ValueError."""
        with pytest.raises(ValueError, match="Invalid bottom_boundary_condition"):
            EnvironmentConfig(bottom_boundary_condition='invalid_boundary')

    def test_invalid_surface_boundary_condition(self):
        """Test that invalid surface boundary condition raises ValueError."""
        with pytest.raises(ValueError, match="Invalid surface_boundary_condition"):
            EnvironmentConfig(surface_boundary_condition='invalid_boundary')

    def test_valid_boundary_condition_options(self):
        """Test that all valid boundary condition options work."""
        valid_options = ['vacuum', 'acousto-elastic', 'rigid', 'from-file', 'default']
        for option in valid_options:
            config = EnvironmentConfig(bottom_boundary_condition=option)
            assert config.bottom_boundary_condition == option

    def test_valid_surface_boundary_condition_options(self):
        """Test that all valid boundary condition options work."""
        valid_options = ['vacuum', 'acousto-elastic', 'rigid', 'from-file', 'default']
        for option in valid_options:
            config = EnvironmentConfig(surface_boundary_condition=option)
            assert config.surface_boundary_condition == option

    def test_invalid_grid_type(self):
        """Test that invalid grid type raises ValueError."""
        with pytest.raises(ValueError, match="Invalid grid"):
            EnvironmentConfig(grid='invalid_grid')

    def test_valid_grid_options(self):
        """Test that all valid grid options work."""
        valid_options = ['rectilinear', 'irregular', 'default']
        for option in valid_options:
            config = EnvironmentConfig(grid=option)
            assert config.grid == option

    def test_invalid_beam_type(self):
        """Test that invalid beam type raises ValueError."""
        with pytest.raises(ValueError, match="Invalid beam_type"):
            EnvironmentConfig(beam_type='invalid_beam')

    def test_valid_beam_type_options(self):
        """Test that all valid beam type options work."""
        valid_options = ['hat-cartesian', 'hat-ray', 'gaussian-cartesian', 'gaussian-ray', 'default']
        for option in valid_options:
            config = EnvironmentConfig(beam_type=option)
            assert config.beam_type == option

    def test_invalid_attenuation_units(self):
        """Test that invalid attenuation units raise ValueError."""
        with pytest.raises(ValueError, match="Invalid attenuation_units"):
            EnvironmentConfig(attenuation_units='invalid_units')

    def test_valid_attenuation_units_options(self):
        """Test that all valid attenuation units options work."""
        valid_options = [
            'nepers per meter', 'frequency dependent', 'dB per meter',
            'frequency scaled dB per meter', 'dB per wavelength',
            'quality factor', 'loss parameter', 'default'
        ]
        for option in valid_options:
            config = EnvironmentConfig(attenuation_units=option)
            assert config.attenuation_units == option

    def test_invalid_volume_attenuation(self):
        """Test that invalid volume attenuation raises ValueError."""
        with pytest.raises(ValueError, match="Invalid volume_attenuation"):
            EnvironmentConfig(volume_attenuation='invalid_attenuation')

    def test_valid_volume_attenuation_options(self):
        """Test that all valid volume attenuation options work."""
        valid_options = ['thorp', 'francois-garrison', 'biological', 'none']
        for option in valid_options:
            config = EnvironmentConfig(volume_attenuation=option)
            assert config.volume_attenuation == option


class TestDataclassIntegration:
    """Test integration of dataclass validation with existing functions."""

    def test_create_env2d_with_validation(self):
        """Test that create_env2d works with valid options and validation."""
        env = bh.create_env2d(
            depth=40,
            soundspeed=1540,
            soundspeed_interp='linear'
        )
        assert isinstance(env, dict)
        assert env['depth'] == 40
        assert env['soundspeed'] == 1540
        assert env['soundspeed_interp'] == 'linear'

    def test_create_env2d_with_invalid_options(self):
        """Test that create_env2d fails with invalid options."""
        with pytest.raises(ValueError, match="Invalid soundspeed_interp"):
            bh.create_env2d(soundspeed_interp='invalid_option')

    def test_check_env2d_with_dataclass_validation(self):
        """Test that check_env2d uses dataclass validation."""
        # Create an environment with invalid option
        env = bh.create_env2d()
        env['soundspeed_interp'] = 'invalid_option'

        # Should raise ValueError due to dataclass validation
        with pytest.raises(ValueError, match="Invalid soundspeed_interp"):
            bh.check_env2d(env)

    def test_backward_compatibility_preserved(self):
        """Test that existing dictionary-based interface still works."""
        # This should work exactly as before
        env = bh.create_env2d(depth=40, soundspeed=1540)
        env = bh.check_env2d(env)
        assert env['depth'] == 40
        assert env['soundspeed'].iloc[0,0] == 1540


class TestTransmissionLossValidation:
    """Test validation of transmission loss mode and source type."""

    def test_validate_transmission_loss_mode_valid(self):
        """Test that valid transmission loss modes pass validation."""
        valid_modes = ['coherent', 'incoherent', 'semicoherent']
        for mode in valid_modes:
            # Should not raise exception
            _validate_transmission_loss_mode(mode)

    def test_validate_transmission_loss_mode_invalid(self):
        """Test that invalid transmission loss modes raise ValueError."""
        with pytest.raises(ValueError, match="Invalid transmission loss mode"):
            _validate_transmission_loss_mode('invalid_mode')

    def test_validate_source_type_valid(self):
        """Test that valid source types pass validation."""
        valid_types = ['point', 'line', 'default']
        for source_type in valid_types:
            # Should not raise exception
            _validate_source_type(source_type)

    def test_validate_source_type_invalid(self):
        """Test that invalid source types raise ValueError."""
        with pytest.raises(ValueError, match="Invalid source type"):
            _validate_source_type('invalid_source')


class TestDataclassUtilities:
    """Test utility functions for dataclass conversion."""

    def test_to_dict_conversion(self):
        """Test conversion of dataclass to dictionary."""
        config = EnvironmentConfig(depth=40, soundspeed=1540)
        env_dict = config.to_dict()

        assert isinstance(env_dict, dict)
        assert env_dict['depth'] == 40
        assert env_dict['soundspeed'] == 1540
        assert 'name' in env_dict
        assert 'type' in env_dict

    def test_from_dict_conversion(self):
        """Test creation of dataclass from dictionary."""
        env_dict = {
            'depth': 40,
            'soundspeed': 1540,
            'soundspeed_interp': 'linear'
        }
        config = EnvironmentConfig.from_dict(env_dict)

        assert config.depth == 40
        assert config.soundspeed == 1540
        assert config.soundspeed_interp == 'linear'

    def test_from_dict_with_invalid_fields(self):
        """Test that from_dict ignores invalid field names."""
        env_dict = {
            'depth': 40,
            'soundspeed': 1540,
            'invalid_field': 'should_be_ignored'
        }
        # Should not raise exception, invalid field should be ignored
        config = EnvironmentConfig.from_dict(env_dict)
        assert config.depth == 40
        assert config.soundspeed == 1540
        # Invalid field should not be present
        assert not hasattr(config, 'invalid_field')
