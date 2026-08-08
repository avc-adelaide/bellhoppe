from scipy.io import loadmat
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import aubellhop as bh
import aubellhop.pyplot as bhp


env2 = bh.Environment(
    frequency = 200,
    beam_num = 1000,
    receiver_depth = 10,
    receiver_range = 80,
)

rays = bh.compute_eigenrays(env2)
fig = plt.figure(figsize=(5,5))
ax = fig.add_subplot()
bhp.pyplot_rays(rays,env=env2,ax=ax)
plt.savefig("fig/demo-erays.pdf")
plt.close()

arr = bh.compute_arrivals(env2)
fig = plt.figure(figsize=(8,5))
ax = fig.add_subplot()
bhp.pyplot_arrivals(arr,ax=ax,dB=True,baseline=-100,colorbar=True)
plt.savefig("fig/demo-arr.pdf", bbox_inches='tight')
plt.close()
