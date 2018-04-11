"""Build a docker compatible tar-format from a local file."""

import io
import logging
import os
import tarfile
import tempfile

from blueprints.dockerfile import docker_string

log = logging.getLogger(__name__)


class CreateFromFile:
    """Create a tar.gz ready to build a docker image from a local file."""

    def __init__(self, file_path: str, base_image: str) -> None:
        self.file_path = file_path
        self.base_image = base_image
        self.tar_tempfile = None

    def __enter__(self):
        """Build and image from a file-like-object."""
        with tarfile.open(self.file_path, 'r') as tarobj:

            self.tar_tempfile = tempfile.TemporaryFile()
            new_tarobj = tarfile.open(mode='w:gz', fileobj=self.tar_tempfile)

            requirements = False

            members = tarobj.getmembers()

            log.info("Copying files.....")

            for member in members:

                # check if a file is "requirements.txt"
                if member.name == "requirements.txt":
                    requirements = True

                if member.name != "Dockerfile":
                    try:
                        file_inside_tar = tarobj.extractfile(member.path)
                        new_tarobj.addfile(member, file_inside_tar)
                    except KeyError:
                        continue

        # add an empty requirements.txt
        # in case is not included
        # to prevent pip install from fail
        if requirements is False:
            file = b"# requirements file\n"
            file_info = tarfile.TarInfo("requirements.txt")
            file_info.size = len(file)
            new_tarobj.addfile(file_info, io.BytesIO(file))

        # add dockerfile
        docker_file = docker_string.format(
            image=self.base_image).encode("utf-8")
        docker_file_info = tarfile.TarInfo("Dockerfile")
        docker_file_info.size = len(docker_file)
        new_tarobj.addfile(docker_file_info, io.BytesIO(docker_file))

        # close the tar object
        new_tarobj.close()

        log.info(f"Tar {self.file_path} creation completed.")

        self.tar_tempfile.seek(0)
        return self.tar_tempfile

    def __exit__(self, exc_type, exc, tb):
        """Close the tempfile and remove the uploaded file."""
        self.tar_tempfile.close()
        os.remove(self.file_path)
        log.info(f"File {self.file_path} removed.")
