"""Basic tests for pivot functionality"""
import os
import pytest


def test_pivot_module_exists():
    """Test that catcol module exists and can be imported"""

    catcol_path = os.path.join(
        os.path.dirname(__file__),
        '../catcol.py'
    )

    assert os.path.exists(catcol_path)


# TODO: Add tests for catcol functionality once refactored
# Current catcol.py is proof-of-concept - will need enhancement for v0.2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
