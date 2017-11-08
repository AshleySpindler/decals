import pytest

from astropy.io import fits
import matplotlib.pyplot as plt

from get_images.image_utils import dstn_rgb, get_rgb, lupton_rgb


@pytest.fixture()
def fits_loc():
    return 'python/test_examples/example_a.fits'


@pytest.fixture()
def jpeg_loc():
    return 'python/test_examples/test_output.jpg'


def image_data_by_band(fits_loc):
    img = fits.getdata(fits_loc)
    return (img[0, :, :], img[1, :, :], img[2, :, :])


@pytest.fixture()
def jpeg_creation_params():
    # Set parameters for RGB image creation
    return {
        'scales': dict(
            g=(2, 0.008),
            r=(1, 0.014),
            z=(0, 0.019)),
        'bands': 'grz',
        'mnmx': (-0.5, 300),
        'arcsinh': 1.,
        'desaturate': False
    }


@pytest.fixture()
def dustin_creation_params():
    return dict(
        mnmx=(-1, 100.),
        arcsinh=1.,
        bands='grz')

# def test_dstn_rgb(image_data_by_band, jpeg_creation_params, jpeg_loc):
#
#     rgbimg = dstn_rgb(image_data_by_band, **jpeg_creation_params)
#     plt.imsave(jpeg_loc, rgbimg, origin='lower')


def plot_jpegs(jpegs, name):
    fig, axes = plt.subplots(1, 3)
    for ax_index, ax in enumerate(axes):
        cbar = ax.imshow(jpegs[ax_index])
    # fig.colorbar(cbar)
    plt.tight_layout()
    plt.savefig('python/test_examples/{}.jpg'.format(name))


def test_dstn_rgb_on_varying_brightness():
    original_data_by_band = image_data_by_band('python/test_examples/example_e.fits')
    data_up_20pc = [band * 2. for band in original_data_by_band]
    data_down_20pc = [band * 0.5 for band in original_data_by_band]

    data = [data_down_20pc, original_data_by_band, data_up_20pc]

    desaturate_off = jpeg_creation_params()
    jpegs = [dstn_rgb(image, **desaturate_off) for image in data]
    plot_jpegs(jpegs, 'ours_comparison')

    desaturate_on = desaturate_off
    desaturate_on['desaturate'] = True
    jpegs = [dstn_rgb(image, **desaturate_on) for image in data]
    plot_jpegs(jpegs, 'ours_comparison_desaturate')


def test_decals_on_varying_brightness():
    original_data_by_band = image_data_by_band('python/test_examples/example_e.fits')
    data_up_20pc = [band * 2. for band in original_data_by_band]
    data_down_20pc = [band * 0.5 for band in original_data_by_band]

    data = [data_down_20pc, original_data_by_band, data_up_20pc]

    jpegs = [get_rgb(image, **dustin_creation_params()) for image in data]
    plot_jpegs(jpegs, 'dustin_comparison')


def test_lupton_on_varying_brightness():
    original_data_by_band = image_data_by_band('python/test_examples/example_e.fits')
    data_up_20pc = [band * 2. for band in original_data_by_band]
    data_down_20pc = [band * 0.5 for band in original_data_by_band]

    data = [data_down_20pc, original_data_by_band, data_up_20pc]

    jpegs = [lupton_rgb(image) for image in data]
    plot_jpegs(jpegs, 'lupton_comparison')
