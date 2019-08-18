from collections import OrderedDict

import numpy as np

from matplotlib import cbook, rcParams
from matplotlib.cbook import (
    _OrderedSet, _check_1d, iterable, index_of, get_label)
from matplotlib import docstring
from matplotlib.axes import Axes
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
import matplotlib.transforms as mtransforms
from .spines import Spine
from .axis.baxis import BAxis
from .axis.raxis import RAxis
from .axis.laxis import LAxis

__author__ = 'Yuji Ikeda'


def brl2xy(b, r, l):
    b = np.asarray(b)
    r = np.asarray(r)
    l = np.asarray(l)
    x = b + 0.5 * r
    y = 0.5 * np.sqrt(3.0) * r
    return x, y


def xy2brl(x, y, s=1.0):
    x = np.asarray(x)
    y = np.asarray(y)
    s = np.asarray(s)
    b = s * (x - y / np.sqrt(3.0))
    r = s * (y / np.sqrt(3.0) * 2.0)
    l = s * (1.0 - x - y / np.sqrt(3.0))
    return b, r, l


class TernaryAxesBase(Axes):
    def __init__(self, *args, scale=1.0, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_aspect('equal', adjustable='box', anchor='C')
        self._scale = scale
        self.set_tlim(0.0, scale, 0.0, scale, 0.0, scale)

    def _gen_axes_patch(self):
        """
        Returns the patch used to draw the background of the axes.  It
        is also used as the clipping path for any data elements on the
        axes.

        In the standard axes, this is a rectangle, but in other
        projections it may not be.

        .. note::

            Intended to be overridden by new projection types.

        """
        return mpatches.Polygon(((0.0, 0.0), (1.0, 0.0), (0.5, 1.0)))

    def _gen_axes_spines(self, locations=None, offset=0.0, units='inches'):
        """
        Returns a dict whose keys are spine names and values are
        Line2D or Patch instances. Each element is used to draw a
        spine of the axes.

        In the standard axes, this is a single line segment, but in
        other projections it may not be.

        .. note::

            Intended to be overridden by new projection types.

        """
        return OrderedDict((side, Spine.linear_spine(self, side))
                           for side in ['left', 'right', 'bottom'])

    def get_axes(self):
        return self._axes

    def _get_axis_list(self):
        return (self.baxis, self.raxis, self.laxis)

    def _init_axis(self):
        """Reference: matplotlib/axes/_base.py, _init_axis

        TODO: Manage spines
        """
        self.baxis = BAxis(self)
        self.xaxis = self.baxis
        self.raxis = RAxis(self)
        self.yaxis = self.raxis
        self.laxis = LAxis(self)

        self.spines['bottom'].register_axis(self.baxis)
        self.spines['right'].register_axis(self.raxis)
        self.spines['left'].register_axis(self.laxis)

        self._update_transScale()

    # def get_baxis_text1_transform(self, pad_points):
    #     return (self._ax.transData +
    #             mtransforms.ScaledTranslation(0, -1 * pad_points / 72.0,
    #                                           self.figure.dpi_scale_trans),
    #             "top", "center")

    def get_baxis_text1_transform(self, pad_points):
        return (self._axes.transData +
                mtransforms.ScaledTranslation(-0.5 * pad_points / 72.0, -np.sqrt(3.0) * 0.5 * pad_points / 72.0,
                                              self.figure.dpi_scale_trans),
                "top", "center")

    def get_raxis_text1_transform(self, pad_points):
        return (self._axes.transData +
                mtransforms.ScaledTranslation(1 * pad_points / 72.0, 0,
                                              self.figure.dpi_scale_trans),
                "center_baseline", "left")

    def get_laxis_text1_transform(self, pad_points):
        return (self._axes.transData +
                mtransforms.ScaledTranslation(-0.5 * pad_points / 72.0, np.sqrt(3.0) * 0.5 * pad_points / 72.0,
                                              self.figure.dpi_scale_trans),
                "baseline", "right")

    def get_baxis(self):
        """Return the BAxis instance"""
        return self.baxis

    def get_raxis(self):
        """Return the RAxis instance"""
        return self.raxis

    def get_laxis(self):
        """Return the LAxis instance"""
        return self.laxis

    def cla(self):
        self._blim = (0.0, 1.0)
        self._rlim = (0.0, 1.0)
        self._llim = (0.0, 1.0)
        super().cla()

    @docstring.dedent_interpd
    def grid(self, b=None, which='major', axis='both', **kwargs):
        """
        Configure the grid lines.

        Parameters
        ----------
        b : bool or None, optional
            Whether to show the grid lines. If any *kwargs* are supplied,
            it is assumed you want the grid on and *b* will be set to True.

            If *b* is *None* and there are no *kwargs*, this toggles the
            visibility of the lines.

        which : {'major', 'minor', 'both'}, optional
            The grid lines to apply the changes on.

        axis : {'both', 'b', 'r', 'l'}, optional
            The axis to apply the changes on.

        **kwargs : `.Line2D` properties
            Define the line properties of the grid, e.g.::

                grid(color='r', linestyle='-', linewidth=2)

            Valid *kwargs* are

        %(_Line2D_docstr)s

        Notes
        -----
        The axis is drawn as a unit, so the effective zorder for drawing the
        grid is determined by the zorder of each axis, not by the zorder of the
        `.Line2D` objects comprising the grid.  Therefore, to set grid zorder,
        use `.set_axisbelow` or, for more control, call the
        `~matplotlib.axis.Axis.set_zorder` method of each axis.
        """
        if len(kwargs):
            b = True
        cbook._check_in_list(['b', 'r', 'l', 'both'], axis=axis)
        if axis in ['b', 'both']:
            self.baxis.grid(b, which=which, **kwargs)
        if axis in ['r', 'both']:
            self.raxis.grid(b, which=which, **kwargs)
        if axis in ['l', 'both']:
            self.laxis.grid(b, which=which, **kwargs)

    def _get_corner_points(self):
        scale = self._scale
        points = [
            [0.0, 0.0],
            [scale, 0.0],
            [0.5 * scale, np.sqrt(3.0) * 0.5 * scale],
            ]
        return np.array(points)

    def set_tlim(self, bmin, bmax, rmin, rmax, lmin, lmax, *args, **kwargs):
        """

        Notes
        -----
        xmin, xmax : holizontal limits of the triangle
        ymin, ymax : bottom and top of the triangle
        """
        b = bmax + rmin + lmin
        r = bmin + rmax + lmin
        l = bmin + rmin + lmax
        s = self._scale
        if (abs(b - s) > 1e-12) or (abs(r - s) > 1e-12) or (abs(l - s) > 1e-12):
            raise ValueError(b, r, l, s)
        ax = self._axes

        xmin = bmin + 0.5 * rmin
        xmax = bmax + 0.5 * rmin
        ax.set_xlim(xmin, xmax, *args, **kwargs)

        ymin = 0.5 * np.sqrt(3.0) * rmin
        ymax = 0.5 * np.sqrt(3.0) * rmax
        ax.set_ylim(ymin, ymax, *args, **kwargs)

        self._blim = (bmin, bmax)
        self._rlim = (rmin, rmax)
        self._llim = (lmin, lmax)

    def get_blim(self):
        return self._blim

    def get_rlim(self):
        return self._rlim

    def get_llim(self):
        return self._llim


class TernaryAxes(TernaryAxesBase):
    """
    A ternary graph projection, where the input dimensions are *b*, *r*, *l*.
    The plot starts from the bottom and goes anti-clockwise.
    """
    name = 'ternary'

    def get_blabel(self):
        """
        Get the blabel text string.
        """
        label = self.baxis.get_label()
        return label.get_text()

    def set_blabel(self, blabel, fontdict=None, labelpad=None, **kwargs):
        if labelpad is not None:
            self.baxis.labelpad = labelpad
        return self.baxis.set_label_text(blabel, fontdict, **kwargs)

    def get_rlabel(self):
        """
        Get the rlabel text string.
        """
        label = self.raxis.get_label()
        return label.get_text()

    def set_rlabel(self, rlabel, fontdict=None, labelpad=None, **kwargs):
        if labelpad is not None:
            self.raxis.labelpad = labelpad
        return self.raxis.set_label_text(rlabel, fontdict, **kwargs)

    def get_llabel(self):
        """
        Get the llabel text string.
        """
        label = self.laxis.get_label()
        return label.get_text()

    def set_llabel(self, llabel, fontdict=None, labelpad=None, **kwargs):
        if labelpad is not None:
            self.laxis.labelpad = labelpad
        return self.laxis.set_label_text(llabel, fontdict, **kwargs)

    def text(self, b, r, l, s, *args, **kwargs):
        x, y = brl2xy(b, r, l)
        return super().text(x, y, s, *args, **kwargs)

    def text_xy(self, x, y, s, *args, **kwargs):
        super().text(x, y, s, *args, **kwargs)

    def axbline(self, b=0, **kwargs):
        s = self._scale
        rmin = self.get_rlim()[0]
        lmin = self.get_llim()[0]
        xmin, ymin = brl2xy(b, rmin, s - lmin - b)
        xmax, ymax = brl2xy(b, s - rmin - b, lmin)
        l = mlines.Line2D([xmin, xmax], [ymin, ymax], **kwargs)
        self.add_line(l)
        return l

    def axrline(self, r=0, **kwargs):
        s = self._scale
        lmin = self.get_llim()[0]
        bmin = self.get_blim()[0]
        xmin, ymin = brl2xy(s - bmin - r, r, lmin)
        xmax, ymax = brl2xy(bmin, r, s - lmin - r)
        l = mlines.Line2D([xmin, xmax], [ymin, ymax], **kwargs)
        self.add_line(l)
        return l

    def axlline(self, l=0, **kwargs):
        s = self._scale
        bmin = self.get_blim()[0]
        rmin = self.get_rlim()[0]
        xmin, ymin = brl2xy(bmin, s - rmin - l, l)
        xmax, ymax = brl2xy(s - bmin - l, rmin, l)
        l = mlines.Line2D([xmin, xmax], [ymin, ymax], **kwargs)
        self.add_line(l)
        return l

    def axbspan(self, bmin, bmax, **kwargs):
        s = self._scale
        rmin = self.get_rlim()[0]
        lmin = self.get_llim()[0]
        x0, y0 = brl2xy(bmin, rmin, s - lmin - bmin)
        x1, y1 = brl2xy(bmin, s - rmin - bmin, lmin)
        x2, y2 = brl2xy(bmax, s - rmin - bmax, lmin)
        x3, y3 = brl2xy(bmax, rmin, s - lmin - bmax)

        verts = (x0, y0), (x1, y1), (x2, y2), (x3, y3)
        p = mpatches.Polygon(verts, **kwargs)
        self.add_patch(p)
        return p

    def axrspan(self, rmin, rmax, **kwargs):
        s = self._scale
        lmin = self.get_llim()[0]
        bmin = self.get_blim()[0]
        x0, y0 = brl2xy(s - bmin - rmin, rmin, lmin)
        x1, y1 = brl2xy(bmin, rmin, s - lmin - rmin)
        x2, y2 = brl2xy(bmin, rmax, s - lmin - rmax)
        x3, y3 = brl2xy(s - bmin - rmax, rmax, lmin)

        verts = (x0, y0), (x1, y1), (x2, y2), (x3, y3)
        p = mpatches.Polygon(verts, **kwargs)
        self.add_patch(p)
        return p

    def axlspan(self, lmin, lmax, **kwargs):
        s = self._scale
        bmin = self.get_blim()[0]
        rmin = self.get_rlim()[0]
        x0, y0 = brl2xy(bmin, s - rmin - lmin, lmin)
        x1, y1 = brl2xy(s - bmin - lmin, rmin, lmin)
        x2, y2 = brl2xy(s - bmin - lmax, rmin, lmax)
        x3, y3 = brl2xy(bmin, s - rmin - lmax, lmax)

        verts = (x0, y0), (x1, y1), (x2, y2), (x3, y3)
        p = mpatches.Polygon(verts, **kwargs)
        self.add_patch(p)
        return p

    def plot(self, b, r, l, *args, **kwargs):
        x, y = brl2xy(b, r, l)
        return super().plot(x, y, *args, **kwargs)

    def scatter(self, b, r, l, *args, **kwargs):
        x, y = brl2xy(b, r, l)
        return super().scatter(x, y, *args, **kwargs)

    def hexbin(self, b, r, l, *args, **kwargs):
        x, y = brl2xy(b, r, l)
        return super().hexbin(x, y, *args, **kwargs)

    def quiver(self, b, r, l, db, dr, dl, *args, **kwargs):
        x, y = brl2xy(b, r, l)
        u, v = brl2xy(b + db, r + dr, l + dl)
        u -= x
        v -= y
        return super().quiver(x, y, u, v, *args, **kwargs)

    def fill(self, b, r, l, *args, **kwargs):
        x, y = brl2xy(b, r, l)
        return super().fill(x, y, *args, **kwargs)

    def tricontour(self, b, r, l, *args, **kwargs):
        x, y = brl2xy(b, r, l)
        return super().tricontour(x, y, *args, **kwargs)

    def tricontourf(self, b, r, l, *args, **kwargs):
        x, y = brl2xy(b, r, l)
        return super().tricontourf(x, y, *args, **kwargs)

    def tripcolor(self, b, r, l, *args, **kwargs):
        x, y = brl2xy(b, r, l)
        return super().tripcolor(x, y, *args, **kwargs)

    def triplot(self, b, r, l, *args, **kwargs):
        x, y = brl2xy(b, r, l)
        tplot = self.plot
        self.plot = super().plot
        tmp = super().triplot(x, y, *args, **kwargs)
        self.plot = tplot
        return tmp
