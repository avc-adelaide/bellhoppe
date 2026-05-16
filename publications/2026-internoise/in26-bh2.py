
from scipy.io import loadmat
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

path = "../../docs/quarto/2000a-000b-uwa.series"

with open(path) as f:
    lines = f.readlines()
begins = [i for i, line in enumerate(lines) if "!!! Begin !!!" in line]
ends   = [i for i, line in enumerate(lines) if "!!! End !!!" in line]

block = lines[begins[0]+1 : ends[0]]
data = np.loadtxt(block, delimiter=",")
print(data[:5])
dist_m = data[:,0]
alti_ice = data[:,1]
alti_ice = alti_ice - min(alti_ice) # ensure 0 is highest point
ice_data = np.column_stack((dist_m, alti_ice))


fig = plt.figure(figsize=(3.5,3))
ax = fig.add_subplot()
ax.set_facecolor("darkblue")
ax.plot(dist_m / 1000, -alti_ice, color='lightblue')
ax.fill_between(
    dist_m / 1000,
    -alti_ice,
    y2=1,
    color='lightblue',
    alpha=0.8,
)
ax.set_xlabel("Distance, km")
ax.set_ylabel("Ice surface profile, m")
ax.set_xlim([0, 2])
ax.set_ylim([-16, 1])
ax.text(1,0,"ICE",ha="center",color="white")
ax.text(1,-12,"WATER",ha="center",color="white")

fig.savefig("fig/ice.pdf",bbox_inches="tight", pad_inches=0.0)
plt.close()


import aubellhop as bh
import aubellhop.pyplot as bhp

print("Calculate rays")

env = bh.Environment(
    source_depth=20,
    surface_depth=ice_data,
    surface_boundary_condition="acousto-elastic",
    surface_soundspeed=3500,
    surface_density=890,
    surface_attenuation=0.4,
    attenuation_units="dB per wavelength",
    beam_num=20,
    beam_angle_min=-45,
    beam_angle_max=45,
    bottom_depth=30,
)

erays = bh.compute_rays(env)

fig = plt.figure(figsize=(3.5,3))
ax = fig.add_subplot()
bhp.pyplot_rays(erays,env=env,ax=ax)
plt.savefig("fig/ice-rays.pdf",bbox_inches="tight", pad_inches=0.0)
plt.close()

print("Calculate transmission loss")

ds = 0.02
freq = 400

env2 = bh.Environment(
    frequency=freq,
    source_depth=20,
    bottom_depth=30,
    receiver_depth=np.arange(0, 30, ds),
    receiver_range=np.arange(0, 100, ds),
    surface_boundary_condition="acousto-elastic",
    surface_soundspeed=3500,
    surface_density=890,
    surface_attenuation=0.4,
    attenuation_units="dB per wavelength",
    beam_angle_min=-89,
    beam_angle_max=89,
)

env = env2.copy()
env.surface_depth=ice_data

icetl = bh.compute_transmission_loss(env,mode="coherent")

fig = plt.figure(figsize=(3.5,3))
ax = fig.add_subplot()
bhp.pyplot_transmission_loss(icetl,env=env,ax=ax,vmin=-60,vmax=0)
fig.savefig("fig/ice-tl.png",bbox_inches="tight", pad_inches=0.0)
plt.close()


print("Calculate transmission loss")

icetl = bh.compute_transmission_loss(env2,mode="coherent")

fig = plt.figure(figsize=(3.5,3))
ax = fig.add_subplot()
bhp.pyplot_transmission_loss(icetl,env=env2,ax=ax,vmin=-60,vmax=0)
fig.savefig("fig/ice-tl-flat.png",bbox_inches="tight", pad_inches=0.0)
plt.close()
