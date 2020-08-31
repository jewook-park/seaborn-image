import pytest

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

import seaborn_image as isns

matplotlib.use("AGG")  # use non-interactive backend for tests

_all = ["top", "bottom", "right", "left"]


@pytest.mark.parametrize(
    "which", ["all", "top", "bottom", "right", "left", ["top", "right"], _all]
)
def test_despine(which):
    f, ax = plt.subplots()

    if which == "all":
        which = _all

    if isinstance(which, list):
        for side in which:
            isns.despine(which=side)
            # assert ax.spines[side] == False
    else:
        isns.despine(which=which)
        # assert ax.spines[which] == False

    plt.close("all")


def test_despine_value():
    plt.subplots()
    with pytest.raises(ValueError):
        isns.despine(which="center")


def test_despine_type():
    plt.subplots()
    with pytest.raises(TypeError):
        isns.despine(which=0)


def test_load_image():
    img = isns.load_image("polymer")
    np.testing.assert_array_equal(
        img, np.loadtxt("data/PolymerImage.txt", skiprows=1) * 1e9
    )

    img = isns.load_image("polymer outliers")
    test_img = np.loadtxt("data/PolymerImage.txt", skiprows=1) * 1e9
    test_img[0, 0] = 80
    np.testing.assert_array_equal(img, test_img)


def test_load_image_error():
    with pytest.raises(ValueError):
        isns.load_image("coins")
