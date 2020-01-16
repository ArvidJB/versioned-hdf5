from uuid import uuid4

from .backend import write_dataset, create_virtual_dataset

# TODO: Allow version_name to be a version group
def create_version(f, version_name, prev_version, datasets,
                   make_current=True):
    """
    Create a new version

    prev_version should be a pre-existing version name, or ''

    datasets should be a dictionary mapping {path: dataset}

    Returns the group for the new version.
    """
    if not prev_version:
        prev_version = '__first_version__'

    if version_name is None:
        version_name = str(uuid4())

    versions = f['_version_data/versions']
    if version_name in versions:
        raise ValueError(f"There is already a version with the name {version_name}")
    if prev_version not in versions:
        raise ValueError(f"Previous version {prev_version!r} not found")

    group = versions.create_group(version_name)
    group.attrs['prev_version'] = prev_version
    if make_current:
        versions.attrs['current_version'] = version_name

    for name, data in datasets.items():
        slices = write_dataset(f, name, data)
        create_virtual_dataset(f, version_name, name, slices)

    return group

def get_nth_prev_version(f, version_name, n):
    versions = f['_version_data/versions']
    if version_name not in versions:
        raise ValueError(f"Version {version_name!r} not found")

    version = version_name
    for i in range(n):
        version = versions[version].attrs['prev_version']

        # __first_version__ is a meta-version and should not be returnable
        if version == '__first_version__':
            raise ValueError(f"{version_name!r} has fewer than {n} versions before it")

    return version
