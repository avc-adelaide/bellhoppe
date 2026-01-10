"""AUBELLHOP: Python interface for the Bellhop underwater acoustic propagation models.

This toolbox uses the Bellhop acoustic propagation model. For this model
to work, the complete aubellhop package must be built and installed
and `bellhop.exe` should be in your PATH.

Copyright (c) 2025-, Will Robertson
Copyright (c) 2018-2025, Mandar Chitre

This file was originally part of arlpy, released under Simplified BSD License.
It has been relicensed in this repository to be compatible with the Bellhop licence (GPL).
"""

from __future__ import annotations

# this format to explicitly mark the functions as public:
from aubellhop.readers import read_ssp as read_ssp
from aubellhop.readers import read_ssp3d as read_ssp3d
from aubellhop.readers import read_ati as read_ati
from aubellhop.readers import read_bty as read_bty
from aubellhop.readers import read_sbp as read_sbp
from aubellhop.readers import read_trc as read_trc
from aubellhop.readers import read_brc as read_brc

from aubellhop.readers import read_rays as read_rays
from aubellhop.readers import read_arrivals as read_arrivals

from aubellhop.environment import Environment as Environment
from aubellhop.models import Models as Models

from aubellhop.compute import compute_from_file as compute_from_file
from aubellhop.compute import compute as compute
from aubellhop.compute import compute_rays as compute_rays
from aubellhop.compute import compute_eigenrays as compute_eigenrays
from aubellhop.compute import compute_arrivals as compute_arrivals
from aubellhop.compute import compute_transmission_loss as compute_transmission_loss
from aubellhop.compute import arrivals_to_impulse_response as arrivals_to_impulse_response

from aubellhop.demo import demo as demo

### Export module names for auto-importing in __init__.py

__all__ = [
    name for name in globals() if not name.startswith("_")  # ignore private names
]
