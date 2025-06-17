import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

x = [[True, False, False], [False, True, True]]

plt.figure()
sns.heatmap(x, cbar=False, square=True, cmap="binary")
plt.axis("off")
plt.savefig("fig.png")
