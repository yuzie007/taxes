# Tips for the Implementation

## Aim of `taxes`

- To use rcParams rather than hard-coded defaults

## Convention in `taxes`

In a ternary plot, three variables which sum to a constant (`ternary_scale`) 
`t` + `l` + `r` = `ternary_scale` (= 1 in taxes by default) are projected onto
a two-dimensional triangle.
Each variable is associated with each corner of the triangle, and the value is
represented by the scaled distance to the corner from its opposite side.

There may be two kinds of perspectives to read a ternary plot; the
"corner-based" and the "side-based" perspectives.
The `taxes` code adopts the "corner-based" perspective.
In this perspective, each of the three variables is associated with a corner of
the triangle, and the position in the triangle is given as the scaled distance
to the corner from its opposite side, as already written above.
In `taxes`, the order of the variables is `T (top) → L (left) → R (right)`
(counterclockwise).

In `taxes`, by default, the ticks are shown to the right side of the triangle
with seeing the corresponding corner upward.
You can put the ticks to the opposite sides by `ax.opposite_ticks(True)`.
Notice that, although the tick positions are changed, still a point in the
triangle corresponds to the same composition.

![](corner_based_1.svg)

![](corner_based_2.svg)

Some people read a ternary plot with the "side-based" perspective like the
figure below. In this perspective, we must also specify if the ticks proceed
in a clockwise or a counterclockwise manner.
*Be careful that a point in the triangle corresponds to different compositions
between the clockwise and the counterclockwise manners*, which could be
confusing.
This also means a position for a side does not immediately associated with the
value of the corresponding variable in the "side-based" perspective.
In `taxes`, therefore, the "corner-based" perspective is adopted.

![](side_based_ccw.svg)

![](side_based_cw.svg)

The discussion
[here](https://github.com/marcharper/python-ternary/issues/13)
and
[here](https://github.com/marcharper/python-ternary/issues/18)
may be also helpful to understand.

## Convention in other software

In the corner-based perspective, [existing codes](alternatives.md) for ternary
plots give the following orders by default:

|Code           |Order of triangle corners|Ticks    |
|---------------|-------------------------|---------|
|Plotly         |`T → L → R` (CCW)        |CW       |
|python-ternary |`R → T → L` (CCW)        |CCW      |
|ggtern         |`L → R → T` (CCW)        |CCW      |
|Ternary (R)    |`T → R → L` (CW)         |CW       |
|d3-ternary     |`L → R → T` (CCW)        |CW       |
|PGFPlots       |`T → L → R` (CCW)        |CCW      |
|Veusz          |`R → L → T` (CW)         |CCW      |
|ternaryplot.com|`T → L → R` (CCW)        |CW       |
|JMP            |`L → T → R` (CW)         |CW       |
|Origin         |`R → T → L` (CCW)        |CCW      |
|Statgraphics   |`T → L → R` (CCW)        |CCW      |

As found, the majority is

- `T → L → R` (CCW) for the order of triangle corners
- CCW for the ticks progress

The `taxes` code decides to follow this convention.

## Scaling

In most plotting methods in `taxes`, the given three variables are
automatically scaled by `ternary_scale`.
By this convention, the three variables can be treated on an equal footing.
The exceptions are the following span-plots:

- `ax.axbline`
- `ax.axrline`
- `ax.axlline`
- `ax.axbspan`
- `ax.axrspan`
- `ax.axlspan`

Since in these methods only one of the variables is given, in principle it is
not possible whether the given value is already scaled or not.
**To avoid any confusions, it is strongly suggested that you scaled the three
variables beforehand outside `taxes`.**

## AxesSubplot

The `AxesSubplot` class is *dynamically* created by
`axes/_subplots.subplot_class_factory`.

In `taxes`, I define `TernaryAxes` without the suffix `Subplot`.

## Tick

### Markers

In `matplotlib`, ticks is defined as the list of `Tick` instances.
Each `Tick` corresponds to a value of the corresponding coordinate and has
three `Line2D` instances to show a tick marker for each side and a grid and
`Text` to show the tick-label.

A tick is shown by a marker.
To make a tilted tick marker, `taxes` rotate/scale the default one in the
`tilt` method.
By default, the tick-maker in `matplotlib` is already scaled as

- 1.0 for `self._tickdir in ['in', 'out']`
- 0.5 for `self._tickdir in ['inout']`

and is already rotated by 90 degrees for the `XTick`.
When tilting the tick-marker, we must also re-apply the following
rotation/scaling to it.

### Remove Round-off

We need to define `_get_pixel_distance_along_axis` in e.g. `BAxis`.

## TernaryTick

- To be simply inherited from `matplotlib.axis.Tick`
    - `get_tick_padding`
    - `get_children`
- To be modified with inheritance
    - `_get_tick1line`, `_get_tick2line`, `_get_gridline`
        - `transform` of the line must be overridden by the one suitable for
        the corresponding axis.
    - `update_position`?
        - So far, tick-angles are modified in this method with calling the
        `tilt` method. This may be however not good when we want to modify the
        tick-label rotations.

## TernaryAxis

- To be overridden
    - `update_label_position`
        - Note that the tick-positions are updated via `_update_ticks`.

### `offsetText`

When, for example, we have a large y-axis values, `matplotlib` shows the value
as the difference from the reference value, with showing it at one end.
The `offsetText` indicates the text showing this reference value.

## BAxis, RAxis, LAxis

- To be overridden
    - `_get_label`
        - The default rotation as well as rotation_mode should be overridden
          depending on the axis type.

## `fig.colorbar`

In `fig.colorbar` in `matplotlib`, the position of the colorbar does not care
y-ticks at the right side.
The keywords `fraction`, `pad` determine the position of the colorbar, which
we specify by hand.
Following to this behavior, `taxes` does NOT provide a function to
automatically position the colorbar.

## Interactive mode

The buttons in the interactive mode call the following methods:
- `Home` calls `_set_view`
- `Pan/Zoom` calls `drag_pan`
- `Zoom-to-rectangle` calls `_set_view_from_bbox`

So, e.g., if you want to scale the axes for ternary plots according to the
change of (`xmin`, `ymin`, `xmax`, `ymax`), you need to override these methods
to additionally call the rescaling method for the axes for ternary
plots (`_set_ternary_lim_from_xlim_and_ylim`).

If you want to prohibit e.g. `Zoom-to-rectanble`, you need to override e.g.
`can_zoom` to return `False`. (`PolarAxes` does this.)