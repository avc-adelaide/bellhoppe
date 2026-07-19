
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

env = bh.Environment(frequency=2000,beam_angle_min=-90,beam_angle_max=90,beam_num=90,receiver_depth = np.arange(-1.0,env.bottom_depth,0.1),receiver_range = np.arange(1.0,100.0,1.0))
env.check()

rays = bh.compute_rays(env)
fig = plt.figure(figsize=(5,5))
ax = fig.add_subplot()
bhp.pyplot_rays(rays,env=env,ax=ax)
plt.savefig("fig/demo-rays.pdf")
plt.close()

env.interference_mode="incoherent"
tl = bh.compute_transmission_loss(env,debug=True)
fig = plt.figure(figsize=(5,5))
ax = fig.add_subplot()
bhp.pyplot_transmission_loss(tl,env=env,ax=ax,vmin=-80,vmax=0)
plt.savefig("fig/demo-tli.pdf")
plt.close()

env.interference_mode="coherent"
tl = bh.compute_transmission_loss(env)
fig = plt.figure(figsize=(5,5))
ax = fig.add_subplot()
bhp.pyplot_transmission_loss(tl,env=env,ax=ax,vmin=-80,vmax=0)
plt.savefig("fig/demo-tlc.pdf")
plt.close()

env.interference_mode="semicoherent"
tl = bh.compute_transmission_loss(env)
fig = plt.figure(figsize=(5,5))
ax = fig.add_subplot()
bhp.pyplot_transmission_loss(tl,env=env,ax=ax,vmin=-80,vmax=0)
plt.savefig("fig/demo-tls.pdf")
plt.close()

env.beam_type = "gaussian-cartesian"
env.interference_mode="semicoherent"
tl = bh.compute_transmission_loss(env)
fig = plt.figure(figsize=(5,5))
ax = fig.add_subplot()
bhp.pyplot_transmission_loss(tl,env=env,ax=ax,vmin=-80,vmax=0)
plt.savefig("fig/demo-tls-gc.pdf")
plt.close()
