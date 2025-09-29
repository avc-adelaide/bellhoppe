"""
Test coverage for edge cases in readers.py

This test file specifically targets the previously uncovered lines in readers.py:
- Line 84-86: Unexpected end of file while reading vector
- Line 117-118: Empty line break condition in _read_ssp_points()
- Line 147-151: ValueError exception handling in SSP parsing
"""

import pytest
import bellhop as bh
import tempfile
import os


def test_parse_vector_unexpected_eof():
    """Test line 84-86: Unexpected end of file while reading vector in _parse_vector()"""
    # Create a malformed .env file that ends abruptly when trying to read a vector
    # The file must end right where _parse_vector is called to read the receiver range count
    env_content = """'Test profile'
50.0
1
'PVF'
51  0.0  5000.0
    0.0  1500.0  /
'A' 0.0
 5000.0  1600.00 0.0 1.0 /
2
1000.0 4000 /
51
0.0 5000.0 /
"""  # File ends when trying to read receiver range count (triggers EOF in _parse_vector)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
        f.write(env_content)
        fname = f.name
    
    try:
        with pytest.raises(ValueError, match="Unexpected end of file while reading vector"):
            bh.read_env2d(fname)
    finally:
        os.unlink(fname)


def test_read_ssp_points_empty_line_break():
    """Test line 117-118: Empty line break condition in _read_ssp_points()"""
    # Create an .env file with an empty line in the SSP section
    # This should trigger the empty line break condition and stop SSP parsing
    env_content = """'Test profile'
50.0
1
'PVF'
51  0.0  5000.0
    0.0  1500.0  /
  200.0  1530.0  /

'A' 0.0
 5000.0  1600.00 0.0 1.0 /
2
1000.0 4000 /
51
0.0 5000.0 /
1001
0.0  100.0 /
'R'
41
-20.0 20.0 /
0.0  5500.0 101.0
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
        f.write(env_content)
        fname = f.name
    
    try:
        # This should successfully parse, stopping at the empty line
        env = bh.read_env2d(fname)
        assert env['name'] == 'Test profile'
        
        # Should have captured the SSP points before the empty line
        assert env['_ssp_env'] is not None
        assert len(env['_ssp_env']) == 2  # Two SSP points before empty line
        
        # Verify the SSP points are correct
        assert env['_ssp_env'][0][0] == 0.0   # First depth
        assert env['_ssp_env'][0][1] == 1500.0  # First sound speed
        assert env['_ssp_env'][1][0] == 200.0   # Second depth
        assert env['_ssp_env'][1][1] == 1530.0  # Second sound speed
    finally:
        os.unlink(fname)


def test_read_ssp_points_value_error_recovery():
    """Test line 147-151: ValueError exception handling in SSP parsing"""
    # This test demonstrates the ValueError recovery mechanism where invalid
    # numerical data in the SSP section gets caught, the line is put back,
    # and parsing continues with that line treated as the next section
    
    # Create an .env file where the bottom boundary line will be mistaken for SSP data,
    # trigger a ValueError, then get put back and processed correctly
    env_content = """'Test profile'
50.0
1
'PVF'
51  0.0  5000.0
    0.0  1500.0  /
  200.0  1530.0  /
'A' 0.0
 5000.0  1600.00 0.0 1.0 /
2
1000.0 4000 /
51
0.0 5000.0 /
1001
0.0  100.0 /
'R'
41
-20.0 20.0 /
0.0  5500.0 101.0
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
        f.write(env_content)
        fname = f.name
    
    try:
        # This should successfully parse. The 'A' line will initially be read as SSP data,
        # trigger a ValueError when trying to parse 'A' as a float, then get put back
        # and correctly processed as the bottom boundary condition
        env = bh.read_env2d(fname)
        assert env['name'] == 'Test profile'
        
        # Should have captured the SSP points before the 'A' line
        assert env['_ssp_env'] is not None
        assert len(env['_ssp_env']) == 2  # Two SSP points before 'A' line
        
        # The 'A' line should have been put back and processed as bottom boundary
        from bellhop.constants import _Strings
        assert env['bottom_boundary_condition'] == _Strings.acousto_elastic  # 'A' maps to acousto_elastic
    finally:
        os.unlink(fname)


def test_comprehensive_edge_cases():
    """Test that all edge cases work together and improve coverage"""
    # This test combines multiple scenarios to ensure robustness
    
    # Test 1: EOF case
    test_parse_vector_unexpected_eof()
    
    # Test 2: Empty line case  
    test_read_ssp_points_empty_line_break()
    
    # Test 3: ValueError recovery case
    test_read_ssp_points_value_error_recovery()


if __name__ == "__main__":
    # Allow running this test file directly
    import sys
    
    try:
        test_parse_vector_unexpected_eof()
        print("✓ EOF test passed")
    except Exception as e:
        print(f"✗ EOF test failed: {e}")
        sys.exit(1)
    
    try:
        test_read_ssp_points_empty_line_break()
        print("✓ Empty line test passed")
    except Exception as e:
        print(f"✗ Empty line test failed: {e}")
        sys.exit(1)
    
    try:
        test_read_ssp_points_value_error_recovery()
        print("✓ ValueError recovery test passed")
    except Exception as e:
        print(f"✗ ValueError recovery test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("All readers.py coverage tests passed!")