
import logging
import datetime

import pandas as pd
from astropy.io import fits
from astropy import table
from astropy.table import Table
from astropy import units as u

from shared_astro_utils import matching_utils, panoptes_utils

from decals.a_download_decals.get_catalogs.get_joint_nsa_decals_catalog import get_nsa_catalog
from decals.a_download_decals.get_images import image_utils
import decals.b_to_zooniverse.to_zooniverse_settings as settings
from decals.b_to_zooniverse.do_upload import upload_subject_set
from decals.b_to_zooniverse.previous_subjects.previous_decals_subjects import get_previous_decals_subjects
from decals.b_to_zooniverse.make_calibration_images.get_calibration_catalog import get_expert_catalog, get_expert_catalog_joined_with_decals
from decals.b_to_zooniverse.make_calibration_images.get_calibration_images import make_catalog_png_images
from decals.b_to_zooniverse.setup.check_joint_catalog import enforce_joint_catalog_columns



def upload_decals_to_panoptes(joint_catalog_all,
                              previous_subjects,
                              expert_catalog,
                              calibration_dir):
    """
    Using the DECALS joint catalog created by a_download_decals, upload DECALS sets to Panoptes
    Only upload new galaxies by checking against previous subjects used
    Create calibration images with different rgb conversions to check if classifications are affected
    Upload the calibration images

    Args:
        joint_catalog (astropy.Table): NSA subjects imaged by DECALS. Includes png_loc, png_ready columns.
        previous_subjects (astropy.Table):
        expert_catalog (astropy.Table): Nair 2010 (human expert) catalog of rings, bars, etc.
        calibration_dir (str): directory to save calibration images
        subject_set_name (str): name to give subject set on Panoptes. Must not already exist.
        new_calibration_images (bool): if True, remake calibration images. If False, do not.

    Returns:
        None
    """

    logging.info('Galaxies in joint catalog: {}'.format(len(joint_catalog_all)))
    logging.info('fits in joint catalog: {}'.format(joint_catalog_all['fits_ready'].sum()))

    dr5_only_galaxies = get_galaxies_safe_for_upload(joint_catalog, previous_subjects)
    # for use by active learning
    del dr5_only_galaxies['absmag']
    del dr5_only_galaxies['petroflux']
    del dr5_only_galaxies['nmgy']
    dr5_only_galaxies.to_pandas().to_csv('/media/mike/beta/decals/catalogs/decals_dr5_uploadable_master_catalog_nov_2019.csv')
    exit()

    # use Nair galaxies previously classified in DR2
    # calibration_catalog = get_expert_catalog_joined_with_decals(dr2_galaxies, expert_catalog)
    # print(len(calibration_catalog))

    # calibration_set_name = 'decals_dr2_nair_calibration_dr2_style_all'

    # calibration_catalog_dr2_style = make_catalog_png_images(
    #     calibration_catalog[:20],
    #     image_utils.get_dr2_style_image,
    #     '{}/{}'.format(calibration_dir, calibration_set_name),
    #     size=424,
    #     overwrite=True)
    """
    upload standard calibration set of Nair/DR2 galaxies, coloured by DR1/2 rules
    """
    # _ = upload_subject_set.upload_nair_calibration_subject_set(
    #     calibration_catalog, calibration_set_name)

    """
    upload all Nair/DR2 galaxies, coloured by Lupton rules
    """
    # calibration_set_name = 'decals_dr2_nair_lupton_style_all'
    # calibration_catalog_lupton_style = make_catalog_png_images(
    #     calibration_catalog,
    #     image_utils.get_colour_style_image,
    #     '{}/{}'.format(calibration_dir, calibration_set_name),
    #     size=424,
    #     overwrite=True)  # places new png in calibration folder under this name
    # upload_subject_set.upload_galaxy_subject_set(
    #     calibration_catalog_lupton_style, calibration_set_name)

    """
    upload all Nair/DR2 galaxies, coloured by DR2 rules
    """
    # calibration_set_name = 'decals_dr2_nair_dr2_style_all'
    # calibration_catalog_dr2_style = make_catalog_png_images(
    #     calibration_catalog,
    #     image_utils.get_dr2_style_image,
    #     '{}/{}'.format(calibration_dir, calibration_set_name),
    #     size=424,
    #     overwrite=False)
    # _ = upload_subject_set.upload_galaxy_subject_set(calibration_catalog_dr2_style, calibration_set_name)

    """
    upload first n DR2-only galaxies
    """
    # dr2_only_name = 'first_1k_decals_dr2'
    # _ = upload_subject_set.upload_galaxy_subject_set(dr2_galaxies[:1000], dr2_only_name)

    """
    upload first n DR5-only galaxies
    """
    # dr5_only_name = 'first_3k_decals_dr5_only'
    # _ = upload_subject_set.upload_galaxy_subject_set(dr5_only_galaxies[:3000], dr5_only_name)
    # dr5_only_name = '3k_to_5k_decals_dr5_only'
    # _ = upload_subject_set.upload_galaxy_subject_set(dr5_only_galaxies[3000:5000], dr5_only_name)
    # dr5_only_name = '10k_to_30k_decals_dr5_only'
    # _ = upload_subject_set.upload_galaxy_subject_set(dr5_only_galaxies[10000:30000], dr5_only_name)

    """
    Upload first n DR5-only galaxies NOT already uploaded
    Must redo exports before uploading new galaxies. 
    Alternative: use endpoint API
    """
    latest_export_date_str = '2018-11-05'
    logging.info('Uploading first n DR5 galaxies NOT already uploaded as of {}'.format(latest_export_date_str))
    latest_workflow_classification_export_loc = '/data/galaxy_zoo/decals/panoptes/reduction/raw/classifications/extracts/{}_panoptes-classifications.csv'.format(latest_export_date_str)
    previous_classifications = pd.read_csv(
        latest_workflow_classification_export_loc,
        dtype={'workflow_id': str},
        parse_dates=['created_at'],
        usecols=['created_at', 'workflow_id', 'subject_ids'])

    latest_subject_extract_loc = '/data/galaxy_zoo/decals/panoptes/reduction/raw/subjects/{}_panoptes-subjects.csv'.format(latest_export_date_str)
    uploaded_subjects = pd.read_csv(
        latest_subject_extract_loc,
        dtype={'workflow_id': str},
        usecols=['workflow_id', 'subject_id', 'metadata', 'locations'])

    subjects_not_yet_added = subjects_not_yet_classified(
        catalog=dr5_only_galaxies,
        subject_extract=uploaded_subjects,
        classification_extract=previous_classifications,
        workflow_id='6122',  # dr5 workflow id
        start_date=datetime.datetime(year=2018, month=3, day=15))  # public launch date of DR5

    logging.info('Galaxies in catalog not yet classified (to upload): {}'.format(len(subjects_not_yet_added)))
    subjects_not_yet_added_name = '5k_subjects_not_yet_classified'
    max_new_subjects = 5000
    _ = upload_subject_set.upload_galaxy_subject_set(subjects_not_yet_added[:max_new_subjects], subjects_not_yet_added_name)
    logging.info('Subject set {} successfully uploaded'.format(subjects_not_yet_added_name))


    """
    Upload all galaxies from custom catalog
    """
    # gordon_galaxies = Table.from_pandas(pd.read_csv('/Data/repos/decals/python/z_analysis/gordon_galaxies_sample_2_unique.csv'))
    # custom_catalog_maybe_duplicate, lost = matching_utils.match_galaxies_to_catalog_table(
    #     galaxies=gordon_galaxies,
    #     catalog=joint_catalog_all,
    #     galaxy_suffix='',
    #     catalog_suffix='_dr5',
    #     matching_radius=10. * u.arcsec
    # )
    # logging.warning('Missing: {} from custom catalog!'.format(len(lost)))
    # custom_catalog = table.unique(custom_catalog_maybe_duplicate, keys='iauname', keep='first')
    # custom_catalog_name = 'yjan_gordon_sdss_sample_sept_1100ish'
    # _ = upload_subject_set.upload_galaxy_subject_set(custom_catalog, custom_catalog_name)


def get_galaxies_safe_for_upload(joint_catalog, previous_subjects):
    dr2_galaxies, dr5_only_galaxies = matching_utils.match_galaxies_to_catalog_table(  # unmatched galaxies are new
        galaxies=joint_catalog,
        catalog=previous_subjects,
        galaxy_suffix='',
        catalog_suffix='_dr1_2')  # if field exists in both catalogs

    logging.info('Previously classified galaxies: {}'.format(len(dr2_galaxies)))
    logging.info('New galaxies: {}'.format(len(dr5_only_galaxies)))

    dr5_only_galaxies = dr5_only_galaxies[dr5_only_galaxies['png_ready'] == True]
    dr5_only_galaxies = dr5_only_galaxies[dr5_only_galaxies['fits_filled'] == True]
    logging.info(f'Galaxies safe for upload: {len(dr5_only_galaxies)}')

    return dr5_only_galaxies


def subjects_not_yet_classified(catalog, subject_extract, classification_extract, workflow_id, start_date):
    # TODO temporary until I track down the logging level switch
    logging.basicConfig(
        level=logging.INFO)
    """
    Filter for galaxies in catalog that are not classified
    Will return uploaded galaxies with 0 classifications. Do not run with fresh subject batch.
    Args:
        catalog (astropy.Table): all galaxies, with metadata for upload
        subject_extract (pd.DataFrame): Panoptes subject extract
        classification_extract (pd.DataFrame): Panoptes classification extract
        workflow_id (str): filter classifications and subjects to be from workflow id
        start_date (datetime.pyi): filter classifications to be made after start_date

    Returns:
        (astropy.Table) galaxies in catalog which have 0 classifications or are not yet uploaded anywhere
    """

    relevant_classifications = classification_extract[
        (pd.to_datetime(classification_extract['created_at']) >= start_date) &
        (classification_extract['workflow_id'].astype(str) == workflow_id)]

    uploaded_subjects = set(relevant_classifications['subject_ids'])
    logging.info('Subjects uploaded since launch: {}'.format(len(uploaded_subjects)))
    # subjects must have at least 1 classification since upload. Don't rapidly re-run this.

    # 'subjects_already_added' includes any subject id duplicates: each workflow will have a row for that subject_id
    subjects_already_added = subject_extract[
        (subject_extract['subject_id'].isin(uploaded_subjects)) &
        (subject_extract['workflow_id'].astype(str) == '6122')
        ]
    logging.info('Unique subjects identified as classified since launch: {}'.format(
        len(subjects_already_added['subject_id'].unique())))

    if not subjects_already_added.empty:
        # get ra and dec from subject metadata
        subjects_already_added = panoptes_utils.load_current_subjects(
            subjects_already_added,
            workflow='6122',
            save_loc='temp.csv')
        _, subjects_not_yet_added = matching_utils.match_galaxies_to_catalog_table(
            galaxies=catalog,
            catalog=Table.from_pandas(subjects_already_added),  # duplicates don't matter here
            galaxy_suffix='',
            catalog_suffix='_from_extract',
            matching_radius=10. * u.arcsec)
    else:
        logging.warning('Found no previously uploaded subjects with relevant classifications - not filtering!')
        subjects_not_yet_added = joint_catalog.copy()

    return subjects_not_yet_added



if __name__ == '__main__':

    logging.basicConfig(
        filename='upload_decals.log',
        filemode='w',
        format='%(asctime)s %(message)s',
        level=logging.INFO)

    new_previous_subjects = False

    joint_catalog_loc = settings.joint_catalog_loc
    joint_catalog = Table(fits.getdata(joint_catalog_loc))
    # warning, requires 6GB+ of memory
    joint_catalog = enforce_joint_catalog_columns(joint_catalog, overwrite_cache=False)

    expert_catalog = get_expert_catalog(settings.expert_catalog_loc, settings.expert_catalog_interpreted_loc)

    if new_previous_subjects:
        raw_previous_subjects = pd.read_csv(settings.previous_subjects_loc)  # MongoDB subject dump to csv from Ouro.
        nsa_v1_0_0 = get_nsa_catalog(settings.nsa_v1_0_0_catalog_loc, '1_0_0')  # takes a while
        previous_subjects = get_previous_decals_subjects(raw_previous_subjects, nsa_v1_0_0)
        previous_subjects.write(settings.subject_loc, overwrite=True)
    else:
        previous_subjects_df = pd.read_csv(settings.subject_loc)
        previous_subjects = Table.from_pandas(previous_subjects_df)  # previously extracted decals subjects

    upload_decals_to_panoptes(
        joint_catalog,
        previous_subjects,
        expert_catalog,
        settings.calibration_dir,
    )
