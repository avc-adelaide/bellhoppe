
import arlpy.uwapm as pm

print(pm.models())

# Title / frequency
freq = 200.0  # Hz

# Sound speed profile (depth [m], speed [m/s])
ssp = [
    (0.0,   1436.0),
    (200.0, 1458.4),
    (300.0, 1460.5),
    (1000.0,1466.7),
    (2000.0,1479.6),
    (2500.0,1487.9),
    (3750.0,1510.4),
]

# Define the environment
env = pm.create_env2d(
    frequency=freq,
    soundspeed=ssp,
    depth=3750.0,    # bottom depth [m]
    tx_depth=100.0,  # source depth [m]
    rx_depth=[0, 3750.0],   # receiver depths [m] (NRD=761 implies a dense sweep; you can sample)
    rx_range=[0, 100.0],    # receiver ranges [km]
)

# Run propagation model
tl = pm.compute_transmission_loss(env, mode="coherent", model="bellhop")

print(tl)