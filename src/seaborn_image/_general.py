import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as ss
from matplotlib import gridspec
from matplotlib.axes import Axes
from matplotlib.cm import get_cmap
from matplotlib.colors import Colormap
from skimage.color import rgb2gray

from ._colormap import _CMAP_QUAL
from ._core import _SetupImage

__all__ = ["imgplot", "imghist"]


def imgplot(
    data,
    ax=None,
    cmap=None,
    gray=None,
    vmin=None,
    vmax=None,
    robust=False,
    perc=(2, 98),
    dx=None,
    units=None,
    dimension=None,
    describe=True,
    cbar=True,
    orientation="v",
    cbar_label=None,
    cbar_ticks=None,
    showticks=False,
    despine=True,
):
    """Plot data as a 2-D image with options to ignore outliers, add scalebar, colorbar, title.

    Parameters
    ----------
    data : array-like
        Image data. Supported array shapes are all `matplotlib.pyplot.imshow` array shapes
    ax : `matplotlib.axes.Axes`, optional
        Matplotlib axes to plot image on. If None, figure and axes are auto-generated, by default None
    cmap : str or `matplotlib.colors.Colormap`, optional
        Colormap for image. Can be a seaborn-image colormap or default matplotlib colormaps or
        any other colormap converted to a matplotlib colormap, by default None
    gray : bool, optional
        If True and data is RGB image, it will be converted to grayscale.
        If True and cmap is None, cmap will be set to "gray", by default None
    vmin : float, optional
        Minimum data value that colormap covers, by default None
    vmax : float, optional
        Maximum data value that colormap covers, by default None
    robust : bool, optional
        If True and vmin or vmax are None, colormap range is calculated
        based on the percentiles defined in `perc` parameter, by default False
    perc : tuple or list, optional
        If `robust` is True, colormap range is calculated based
        on the percentiles specified instead of the extremes, by default (2, 98) -
        2nd and 98th percentiles for min and max values
    dx : float, optional
        Size per pixel of the image data. Specifying `dx` and `units` adds a scalebar
        to the image, by default None
    units : str, optional
        Units of `dx`, by default None
    dimension : str, optional
        dimension of `dx` and `units`, by default None
        Options include (similar to `matplotlib_scalebar`):
            - "si" : scale bar showing km, m, cm, etc.
            - "imperial" : scale bar showing in, ft, yd, mi, etc.
            - "si-reciprocal" : scale bar showing 1/m, 1/cm, etc.
            - "angle" : scale bar showing °, ʹ (minute of arc) or ʹʹ (second of arc)
            - "pixel" : scale bar showing px, kpx, Mpx, etc.
    describe : bool, optional
        Brief statistical description of the data, by default True
    cbar : bool, optional
        Specify if a colorbar is to be added to the image, by default True.
        If `data` is RGB image, cbar is False
    orientation : str, optional
        Specify the orientaion of colorbar, by default "v".
        Options include :
            - 'h' or 'horizontal' for a horizontal colorbar to the bottom of the image.
            - 'v' or 'vertical' for a vertical colorbar to the right of the image.
    cbar_label : str, optional
        Colorbar label, by default None
    cbar_ticks : list, optional
        List of colorbar ticks, by default None
    showticks : bool, optional
        Show image x-y axis ticks, by default False
    despine : bool, optional
        Remove axes spines from image axes as well as colorbar axes, by default True

    Returns
    -------
    `matplotlib.axes.Axes`
        Matplotlib axes where the image is drawn.

    Raises
    ------
    TypeError
        if `cmap` is not str or `matplotlib.colors.Colormap`
    TypeError
        if `ax` is not `matplotlib.axes.Axes`
    TypeError
        if `describe` is not bool
    TypeError
        if `robust` is not bool
    TypeError
        if `cbar` is not bool
    TypeError
        if `orientation` is not str
    TypeError
        if `cbar_label` is not str
    TypeError
        if `showticks` is not bool
    TypeError
        if `despine` is not bool
    AssertionError
        if `len(perc)` is not equal to 2
    AssertionError
        if the first element of `perc` is greater than the second

    Examples
    --------

    Plot image

    .. plot::
        :context: close-figs

        >>> import seaborn_image as isns
        >>> img = isns.load_image("polymer")
        >>> isns.imgplot(img)

    Add a scalebar

    .. plot::
        :context: close-figs

        >>> isns.imgplot(img, dx=15, units="nm")

    Change colormap

    .. plot::
        :context: close-figs

        >>> isns.imgplot(img, cmap="deep")

    Rescale colormap to exclude outliers while plotting

    Image with outliers

    .. plot::
        :context: close-figs

        >>> img_out = isns.load_image("polymer outliers")
        >>> isns.imgplot(img_out)

    Rescale colormap using `robust` parameter

    .. plot::
        :context: close-figs

        >>> isns.imgplot(img_out, robust=True, perc=(2,99.99))

    Convert RGB image to grayscale

    .. plot::
        :context: close-figs

        >>> from skimage.data import astronaut
        >>> isns.imgplot(astronaut(), gray=True)

    Change colorbar orientation

    .. plot::
        :context: close-figs

        >>> isns.imgplot(img, orientation="h") # horizontal

    .. plot::
        :context: close-figs

        >>> isns.imgplot(img, orientation="v") # vertical

    Add colorbar label

    .. plot::
        :context: close-figs

        >>> isns.imgplot(img, cbar_label="Height (nm)")

    Avoid image and colorbar axes despining

    .. plot::
        :context: close-figs

        >>> isns.imgplot(img, despine=False)
    """

    # TODO add vmin, vmax, dx, units to checks
    if cmap is not None:
        if not isinstance(cmap, (str, Colormap)):
            raise TypeError

    if ax is not None:
        if not isinstance(ax, Axes):
            raise TypeError

    if not isinstance(describe, bool):
        raise TypeError

    if not isinstance(robust, bool):
        raise TypeError("'robust' must be either True or False")

    if robust is True:
        assert len(perc) == 2
        assert perc[0] < perc[1]  # order should be (min, max)

    if not isinstance(cbar, bool):
        raise TypeError

    if not isinstance(orientation, str):
        raise TypeError

    if cbar_label is not None:
        if not isinstance(cbar_label, str):
            raise TypeError

    if not isinstance(showticks, bool):
        raise TypeError

    if not isinstance(despine, bool):
        raise TypeError

    if isinstance(data, np.ndarray):
        if data.ndim == 3:
            cbar = False  # set cbar to False if RGB image
            robust = False  # set robust to False if RGB image
            if gray is True:  # if gray is True, convert to grayscale
                data = rgb2gray(data)

    if gray is True and cmap is None:  # set colormap to gray only if cmap is None
        cmap = "gray"

    img_plotter = _SetupImage(
        data=data,
        ax=ax,
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        robust=robust,
        perc=perc,
        dx=dx,
        units=units,
        dimension=dimension,
        cbar=cbar,
        orientation=orientation,
        cbar_label=cbar_label,
        cbar_ticks=cbar_ticks,
        showticks=showticks,
        despine=despine,
    )

    f, ax, cax = img_plotter.plot()

    if describe:
        result = ss.describe(data.flatten())
        print(f"No. of Obs. : {result.nobs}")
        print(f"Min. Value : {result.minmax[0]}")
        print(f"Max. Value : {result.minmax[1]}")
        print(f"Mean : {result.mean}")
        print(f"Variance : {result.variance}")
        print(f"Skewness : {result.skewness}")

    return ax


# TODO implement a imgdist function with more distributions (?)
def imghist(
    data,
    cmap=None,
    bins=None,
    vmin=None,
    vmax=None,
    robust=False,
    perc=(2, 98),
    dx=None,
    units=None,
    dimension=None,
    describe=True,
    cbar=True,
    orientation="v",
    cbar_label=None,
    cbar_ticks=None,
    showticks=False,
    despine=True,
    height=5,
    aspect=1.75,
):
    """Plot data as a 2-D image with histogram showing the distribution of
    the data. Options to add scalebar, colorbar, title.

    Parameters
    ----------
    data : array-like
        Image data. Supported array shapes are all `matplotlib.pyplot.imshow` array shapes
    bins : int, optional
        Histogram bins, by default None. If None, `auto` is used.
    ax : `matplotlib.axes.Axes`, optional
        Matplotlib axes to plot image on. If None, figure and axes are auto-generated, by default None
    cmap : str or `matplotlib.colors.Colormap`, optional
        Colormap for image. Can be a seaborn-image colormap or default matplotlib colormaps or
        any other colormap converted to a matplotlib colormap, by default None
    gray : bool, optional
        If True and data is RGB image, it will be converted to grayscale.
        If True and cmap is None, cmap will be set to "gray", by default None
    vmin : float, optional
        Minimum data value that colormap covers, by default None
    vmax : float, optional
        Maximum data value that colormap covers, by default None
    robust : bool, optional
        If True and vmin or vmax are None, colormap range is calculated
        based on the percentiles defined in `perc` parameter, by default False
    perc : tuple or list, optional
        If `robust` is True, colormap range is calculated based
        on the percentiles specified instead of the extremes, by default (2, 98) -
        2nd and 98th percentiles for min and max values
    dx : float, optional
        Size per pixel of the image data. Specifying `dx` and `units` adds a scalebar
        to the image, by default None
    units : str, optional
        Units of `dx`, by default None
    dimension : str, optional
        dimension of `dx` and `units`, by default None
        Options include (similar to `matplotlib_scalebar`):
            - "si" : scale bar showing km, m, cm, etc.
            - "imperial" : scale bar showing in, ft, yd, mi, etc.
            - "si-reciprocal" : scale bar showing 1/m, 1/cm, etc.
            - "angle" : scale bar showing °, ʹ (minute of arc) or ʹʹ (second of arc)
            - "pixel" : scale bar showing px, kpx, Mpx, etc.
    describe : bool, optional
        Brief statistical description of the data, by default True
    cbar : bool, optional
        Specify if a colorbar is to be added to the image, by default True.
        If `data` is RGB image, cbar is False
    orientation : str, optional
        Specify the orientaion of colorbar, by default "v".
        Options include :
            - 'h' or 'horizontal' for a horizontal colorbar to the bottom of the image.
            - 'v' or 'vertical' for a vertical colorbar to the right of the image.
    cbar_label : str, optional
        Colorbar label, by default None
    cbar_ticks : list, optional
        List of colorbar ticks, by default None
    showticks : bool, optional
        Show image x-y axis ticks, by default False
    despine : bool, optional
        Remove axes spines from image axes as well as colorbar axes, by default True
    height : int or float, optional
        Size of the individual images, by default 5.
    aspect : int or float, optional
        Aspect ratio of individual images, by default 1.75.

    Returns
    -------
    `matplotlib.figure.Figure`
        Matplotlib figure.

    Raises
    ------
    TypeError
        if `bins` is not a positive integer

    Examples
    --------

    Plot distribution alongside the image

    .. plot::
        :context: close-figs

        >>> import seaborn_image as isns
        >>> img = isns.load_image("polymer")
        >>> isns.imghist(img)

    Change the orientation

    .. plot::
        :context: close-figs

        >>> isns.imghist(img, orientation="h")

    Change the number of bins

    .. plot::
        :context: close-figs

        >>> isns.imghist(img, bins=300)

    Change height and aspect ratio of the figure

    .. plot::
        :context: close-figs

        >>> isns.imghist(img, height=4, aspect=1.5)

    Add a scalebar

    .. plot::
        :context: close-figs

        >>> isns.imghist(img, dx=15, units="nm")

    Change colormaps

    .. plot::
        :context: close-figs

        >>> isns.imghist(img, cmap="ice")
    """

    if bins is None:
        bins = "auto"
    else:
        if not isinstance(bins, int):
            raise TypeError("'bins' must be a positive integer")
        if not bins > 0:
            raise ValueError("'bins' must be a positive integer")

    if orientation in ["v", "vertical"]:
        orientation = "vertical"  # matplotlib doesn't support 'v'
        f = plt.figure(figsize=(height * aspect, height))
        gs = gridspec.GridSpec(1, 2, width_ratios=[height - 1, 1], figure=f)

    elif orientation in ["h", "horizontal"]:
        orientation = "horizontal"  # matplotlib doesn't support 'h'
        f = plt.figure(figsize=(height, height * aspect))
        gs = gridspec.GridSpec(2, 1, height_ratios=[height - 1, 1], figure=f)

    else:
        raise ValueError(
            "'orientation' must be either : 'horizontal' or 'h' / 'vertical' or 'v'"
        )

    ax1 = f.add_subplot(gs[0])

    ax1 = imgplot(
        data,
        ax=ax1,
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        robust=robust,
        perc=perc,
        dx=dx,
        units=units,
        dimension=dimension,
        describe=describe,
        cbar=cbar,
        orientation=orientation,
        cbar_label=cbar_label,
        cbar_ticks=cbar_ticks,
        showticks=showticks,
        despine=despine,
    )

    # get colorbar axes
    cax = f.axes[1]

    if orientation == "vertical":
        ax2 = f.add_subplot(gs[1], sharey=cax)

        n, bins, patches = ax2.hist(
            data.ravel(), bins=bins, density=True, orientation="horizontal"
        )

    elif orientation == "horizontal":
        ax2 = f.add_subplot(gs[1], sharex=cax)

        n, bins, patches = ax2.hist(
            data.ravel(), bins=bins, density=True, orientation="vertical"
        )

    if not showticks:
        ax2.get_xaxis().set_visible(False)
        ax2.get_yaxis().set_visible(False)

    ax2.set_frame_on(False)

    if cmap is None:
        cm = get_cmap()
    else:
        if cmap in _CMAP_QUAL.keys():
            cm = _CMAP_QUAL.get(cmap).mpl_colormap
        else:
            cm = plt.cm.get_cmap(cmap)

    bin_centers = bins[:-1] + bins[1:]

    # scale values to interval [0,1]
    col = bin_centers - np.min(bin_centers)
    col /= np.max(col)

    for c, p in zip(col, patches):
        plt.setp(p, "facecolor", cm(c))

    return f
