"""
===================
With seaborn styles
===================

You can use seaborn styles with Mpltern in the same way as Matplotlib.
"""
import matplotlib.pyplot as plt
from mpltern.datasets import get_spiral
import seaborn as sns


sns.set_style('darkgrid')

fig = plt.figure()
ax = fig.add_subplot(projection='ternary')

ax.plot(*get_spiral())

ax.set_tlabel('Top')
ax.set_llabel('Left')
ax.set_rlabel('Right')

plt.show()