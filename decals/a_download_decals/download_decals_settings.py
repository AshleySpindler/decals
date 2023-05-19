

def get_bricks_loc(catalog_dir, data_release):
    """
    Returns:
        (str) location of bricks catalog, including center and exposure counts.
            Input file for DR1, DR2. Calculated from brick_coordinates_loc and brick_exposures_loc for DR5.
    """
    if data_release == '5' or data_release == '3':
        bricks_filename = 'survey-bricks-dr{}-with-coordinates.fits'.format(data_release)
    elif data_release == '2':
        bricks_filename = 'decals-bricks-dr2.fits'
    elif data_release == '1':
        bricks_filename = 'decals-bricks-dr1.fits'
    else:
        raise ValueError('Data Release "{}" not recognised'.format(data_release))
    return '{}/{}'.format(catalog_dir, bricks_filename)


data_release = '5'
catalog_dir = '/data/astroml/aspindler/GZ3D/SCRATCH/DECaLS/catalogs'

fits_dir = '/data/astroml/aspindler/GZ3D/SCRATCH/DECaLS/fits_native/dr{}'.format(data_release)
png_dir = '/data/astroml/aspindler/GZ3D/SCRATCH/DECaLS/png_native/dr{}'.format(data_release)

# only needed for dr3+
brick_coordinates_loc = '{}/survey-bricks.fits'.format(catalog_dir)
brick_exposures_loc = '{}/survey-bricks-dr5.fits'.format(catalog_dir)

# if dr3+, brick coordinate-exposure merged catalog will be placed/expected here
bricks_loc = get_bricks_loc(catalog_dir, data_release)

gz3d_catalog_loc = '{}/gz3d_metadata.fits'.format(catalog_dir)

joint_catalog_loc = '{}/gz3d_v{}_decals_dr{}.fits'.format(
            catalog_dir, data_release)

upload_catalog_loc = '{}/dr{}_gz3d_to_upload.fits'.format(catalog_dir, data_release)
