import pandas as pd
from astropy.io import fits
from astropy.table import Table

from download_decals.get_catalogs.get_joint_nsa_decals_catalog import get_nsa_catalog
from download_decals.get_images.download_images_threaded import get_fits_loc, get_jpeg_loc
from make_calibration_images.get_calibration_catalog import get_expert_catalog, get_expert_catalog_joined_with_decals
from make_calibration_images.get_calibration_images import make_calibration_images
from to_zooniverse.create_subject_set import create_prototype_subject_set
from to_zooniverse.identify_new_images import get_new_images
from get_classifications.filter_decals_from_previous_subjects import get_decals_subjects_from_all_subjects

import settings


def upload_decals_to_panoptes(joint_catalog, previous_subjects, nsa_catalog, calibration_dir, new_calibration_images=False):
    """
    Using the DECALS joint catalog created by download_decals, upload DECALS sets to Panoptes
    Only upload new galaxies by checking against previous subjects used
    Create calibration images with different rgb conversions to check if classifications are affected

    etc

    Returns:
        None
    """

    catalog_of_new = get_new_images(joint_catalog, previous_subjects, nsa_catalog)

    calibration_catalog = get_expert_catalog_joined_with_decals(joint_catalog, expert_catalog)
    calibration_catalog = make_calibration_images(calibration_catalog, calibration_dir,
                                                  new_images=new_calibration_images)

    create_prototype_subject_set(catalog_of_new, calibration_catalog)


if __name__ == '__main__':

    if settings.new_previous_subjects:
        all_subjects = pd.read_csv(settings.previous_subjects_loc)
        previous_subjects = get_decals_subjects_from_all_subjects(all_subjects)
        # save for next run
        previous_subjects.to_csv(settings.subject_loc, index=False)
    else:
        previous_subjects = pd.read_csv(settings.subject_loc)  # previously extracted decals subjects

    nsa_catalog = get_nsa_catalog(settings.nsa_catalog_loc, settings.nsa_version)
    joint_catalog = Table(fits.getdata(settings.joint_catalog_loc))
    expert_catalog = get_expert_catalog(settings.expert_catalog_loc)

    # TODO temporary fix, catalog being used has incorrect fits loc
    fits_dir = '/Volumes/external/decals/fits/dr5'
    joint_catalog['fits_loc'] = [get_fits_loc(fits_dir, galaxy) for galaxy in joint_catalog]
    jpeg_dir = '/Volumes/external/decals/jpeg/dr5'
    joint_catalog['jpeg_loc'] = [get_jpeg_loc(jpeg_dir, galaxy) for galaxy in joint_catalog]

    upload_decals_to_panoptes(joint_catalog, previous_subjects, nsa_catalog)
