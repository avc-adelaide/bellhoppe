
from scipy.io import loadmat
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

print("Loading SSP data")

raw = loadmat("../../docs/quarto/lev_ann.mat")
llz = loadmat("../../docs/quarto/lev_latlonZ.mat")

ssp = 1000.0 + raw["c"] / 100.0
lat = 0.1 * llz["lat"].squeeze()
lon = 0.1 * llz["lon"].squeeze()
depth = llz["z"].squeeze()

lat1 = lat.reshape((360, 180), order="F")
lon1 = lon.reshape((360, 180), order="F")

depth_idx = 11
ssp1 = ssp[:, depth_idx].reshape((360, 180), order="F")

# Plot
plt.figure(figsize=(8, 4))
plt.pcolormesh(lon1, lat1, ssp1, shading="auto")
plt.colorbar(label="Sound Speed (m/s)")
plt.xlabel("Longitude (deg)")
plt.ylabel("Latitude (deg)")
plt.gca().set_aspect("equal")
plt.savefig("fig/lev_ssp.pdf")
plt.close()

print("Displaying constant lat")

# Choose a constant longitude (e.g., 150°E)
target_lon = 200.0
lat_min, lat_max = -40, -20

# Mask points
tol = 1  # tolerance in degrees
lon_mask = np.abs(lon - target_lon) < tol
lat_mask = (lat >= lat_min) & (lat <= lat_max)
mask = lon_mask & lat_mask
ssp_subset = ssp[mask, :]
lat_subset = lat[mask]

# Sort by latitude for plotting
sorted_idx = np.argsort(lat_subset)
lat_sorted = lat_subset[sorted_idx]
ssp_sorted = ssp_subset[sorted_idx, :]

# Plot as depth vs latitude
plt.figure(figsize=(6,8))
plt.contourf(lat_sorted, depth, ssp_sorted.T, 50, cmap="viridis")
plt.gca().invert_yaxis()  # depth increases downward
plt.colorbar(label="Sound speed (m/s)")
plt.xlabel("Latitude (°)")
plt.ylabel("Depth (m)")
plt.title(f"Sound speed along longitude {target_lon}°E")
plt.savefig("fig/lev_ssp_lat.pdf")
plt.close()


print("Displaying constant long")

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
plt.figure(figsize=(6,8))
plt.contourf(svp.columns, svp.index, svp, 50, cmap="viridis")
plt.gca().invert_yaxis()  # depth increases downward
plt.colorbar(label="Sound speed (m/s)")
plt.xlabel("Approx. distance (km)")
plt.ylabel("Depth (m)")
plt.title(f"Sound speed along longitude {target_lon}°E")
plt.savefig("fig/lev_ssp_long.pdf")
plt.close()


print("Plotting SSP and rays")

import aubellhop as bh
import aubellhop.pyplot as bhp

svp.columns = distance_km * 1000.0
env = bh.Environment(
  depth=5500,
  soundspeed=svp, # see above for this 2D DataFrame definition
  soundspeed_interp="quadrilateral", # implied
  source_depth=2000,
  receiver_range=40_000,
  receiver_depth=1000,
  beam_angle_min=-89,
  beam_angle_max=89,
)
fig = plt.figure()
ax = fig.add_subplot()
bhp.pyplot_ssp(env,ax=ax)
fig.savefig("fig/lev_ssp_chk.pdf")
plt.close()

erays = bh.compute_eigenrays(env)

fig = plt.figure()
ax = fig.add_subplot()
bhp.pyplot_rays(erays, env=env, ax=ax)
fig.savefig("fig/lev_ssp_rays.pdf")
plt.close()
