
from scipy.io import loadmat
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import aubellhop as bh
import aubellhop.pyplot as bhp

env = bh.Environment(beam_angle_min=-45,beam_angle_max=45)
rays = bh.compute_eigenrays(env)
fig = plt.figure(figsize=(5,5))
ax = fig.add_subplot()
bhp.pyplot_rays(rays,env=env,ax=ax)
plt.savefig("fig/erays-2d.pdf")
plt.close()


env.dimension = "3D"
rays3d = bh.compute_eigenrays(env)

fig = plt.figure(figsize=(6,6))
ax = fig.add_subplot(projection='3d')
bhp.pyplot_rays(rays3d,env=env,ax=ax)
plt.savefig("fig/erays-3d.pdf")
plt.close(fig)
