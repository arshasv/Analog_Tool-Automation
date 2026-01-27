import numpy as np
import matplotlib.pyplot as plt

data = np.loadtxt("rc_tran.csv")
time = data[:, 0]
vout = data[:, 1]

plt.plot(time, vout)
plt.xlabel("Time (s)")
plt.ylabel("Vout (V)")
plt.title("RC Transient Response")
plt.grid(True)
plt.savefig("rc_plot.png")

print("✔ Plot saved as rc_plot.png")

