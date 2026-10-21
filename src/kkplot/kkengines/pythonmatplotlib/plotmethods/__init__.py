
##  plot methods: f( axes, graph, data, columns, auxiliary columns, context)
##  draw the graph directly onto the axes; their return value is stored as
##  the graph's result (consumed by e.g. regression lines)

from .lines import time_line, time_points, time_points_errors, \
    time_cumulativeline, time_bars, time_scatter, time_scatter_columns
from .integratebar import time_integratebar
from .heatmap import time_heatmap
from .raster import time_raster, time_raster_columns
from .regression import time_regressionpoint, time_regressionline, time_regressionzero

PLOTMETHODS = dict(
    time_line=time_line,
    time_points=time_points,
    time_points_errors=time_points_errors,
    time_cumulativeline=time_cumulativeline,
    time_bars=time_bars,
    time_scatter=time_scatter,
    time_integratebar=time_integratebar,
    time_heatmap=time_heatmap,
    time_raster=time_raster,
    time_regressionpoint=time_regressionpoint,
    time_regressionline=time_regressionline,
    time_regressionzero=time_regressionzero)

## plot methods that do not read the graph's data
NODATA_PLOTMETHODS = [ time_regressionline, time_regressionzero]

## column checks that make the whole figure fail (as before)
COLUMNCHECKS = { time_raster: time_raster_columns, time_scatter: time_scatter_columns}
