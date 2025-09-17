BELLHOP Python API Documentation
=================================

This is the Python API documentation for BELLHOP, an underwater acoustic propagation modeling toolbox.

The BELLHOP Python package provides a high-level interface to the BELLHOP acoustic propagation model, 
allowing users to:

* Create and configure underwater acoustic environments
* Compute acoustic ray tracing and field predictions
* Visualize results with modern plotting capabilities
* Read and write BELLHOP-compatible input/output files

Installation
------------

The Python package is included with the BELLHOP distribution. To use it, ensure that:

1. The BELLHOP executables (``bellhop.exe``, ``bellhop3d.exe``) are in your PATH
2. Python dependencies are installed: ``matplotlib``, ``numpy``, ``scipy``, ``pandas``, ``bokeh``

Quick Start
-----------

Here's a simple example of using the BELLHOP Python API:

.. code-block:: python

    import bellhop as bh
    
    # Create a basic underwater environment
    env = bh.create_env2d(
        name='Test Environment',
        frequency=100,  # Hz
        depth=100,      # m
        soundspeed=1500 # m/s
    )
    
    # Compute transmission loss
    tloss = bh.compute_transmission_loss(env)
    
    # Plot results
    bh.plot_transmission_loss(tloss, env)

API Reference
=============

Core Functions
--------------

.. automodule:: bellhop.bellhop
   :members:
   :undoc-members:
   :show-inheritance:

Plotting Utilities
------------------

.. automodule:: bellhop.plot
   :members:
   :undoc-members:
   :show-inheritance:

Module Reference
================

.. automodule:: bellhop
   :members:
   :undoc-members:
   :show-inheritance:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
