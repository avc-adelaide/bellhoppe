
from scipy.io import loadmat
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

print("Loading SSP data")

raw = loadmat("../../docs/quarto/lev_ann.mat")
ssp = 1000.0 + raw["c"] / 100.0

llz = loadmat("../../docs/quarto/lev_latlonZ.mat")
lat = 0.1 * llz["lat"].squeeze()
lon = 0.1 * llz["lon"].squeeze()
depth = llz["z"].squeeze()

lat1 = lat.reshape((360, 180), order="F")
lon1 = lon.reshape((360, 180), order="F")

depth_idx = 11
ssp1 = ssp[:, depth_idx].reshape((360, 180), order="F")

# Plot
plt.figure(figsize=(6, 3.5))
plt.pcolormesh(lon1, lat1, ssp1, shading="auto",
    vmin=1450,
    vmax=1550,
)
plt.colorbar(label="Sound Speed (m/s)",fraction=0.025)
plt.xlabel("Longitude (deg)")
plt.ylabel("Latitude (deg)")
plt.gca().set_aspect("equal")
plt.savefig("fig/lev_ssp.pdf",bbox_inches="tight", pad_inches=0.1)
plt.close()


print("Displaying constant long by distance")

# Choose a constant longitude (e.g., 150°E)
target_lon = 200.5 # must match exactly!
lat_min, lat_max = -40, -20

# Mask points
lon_mask = np.abs(lon - target_lon) < 0.1
lat_mask = (lat >= lat_min) & (lat <= lat_max)
mask = lon_mask & lat_mask
ssp_subset = ssp[mask, :]
lat_subset = lat[mask]

# Sort by latitude for plotting
sorted_idx = np.argsort(lat_subset)
lat_sorted = lat_subset[sorted_idx]
ssp_sorted = ssp_subset[sorted_idx, :]

# 1 degree latitude ≈ 111 km
distance_km = (lat_sorted - lat_sorted[0]) * 111
svp = pd.DataFrame(ssp_sorted.T, columns=distance_km)
svp.index = depth  # distance_km from your latitude slice
plt.figure(figsize=(3.5,3.5))
plt.contourf(svp.columns, svp.index, svp, 50, cmap="viridis")
plt.gca().invert_yaxis()  # depth increases downward
plt.colorbar(label="Sound speed (m/s)")
plt.xlabel("Approx. distance (km)")
plt.ylabel("Depth (m)")
plt.savefig("fig/lev_ssp_long.pdf",bbox_inches="tight", pad_inches=0.1)
plt.close()


print("Plotting SSP and rays")

import aubellhop as bh
import aubellhop.pyplot as bhp

svp.columns = distance_km * 1000.0
env = bh.Environment(
  bottom_depth=5500,
  soundspeed=svp, # see above for this 2D DataFrame definition
  soundspeed_interp="quadrilateral", # implied
  source_depth=2000,
  receiver_range=40_000,
  receiver_depth=1000,
  beam_angle_min=-89,
  beam_angle_max=89,
)
fig = plt.figure(figsize=(3.5,3.5))
ax = fig.add_subplot()
bhp.pyplot_ssp(env,ax=ax)
fig.savefig("fig/lev_ssp_chk.pdf",bbox_inches="tight", pad_inches=0.1)
plt.close()

erays = bh.compute_eigenrays(env)

fig = plt.figure(figsize=(6,3.5))
ax = fig.add_subplot()
bhp.pyplot_rays(erays, env=env, ax=ax)
fig.savefig("fig/lev_ssp_rays.pdf",bbox_inches="tight", pad_inches=0.1)
plt.close()
