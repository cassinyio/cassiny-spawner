"""Build a docker compatible tar-format from s3."""

import io
import logging
import tarfile
import tempfile

import aiobotocore

from blueprints.dockerfile import docker_string

log = logging.getLogger(__name__)


class CreateFromS3:
    """Create a tar.gz ready to build a docker image from S3."""

    def __init__(
        self,
        cargo: str,
        s3_key: str,
        s3_skey: str,
        base_image: str,
        bucket: str="default"
    ) -> None:
        self.bucket = bucket
        self.s3_key = s3_key
        self.s3_skey = s3_skey
        self.cargo = cargo
        self.base_image = base_image

    async def __aenter__(self):
        session = aiobotocore.get_session()

        self.tar_tempfile = tempfile.TemporaryFile()
        tarobj = tarfile.open(mode='w:gz', fileobj=self.tar_tempfile)

        async with session.create_client(
                's3', use_ssl=False,
                endpoint_url=self.cargo,
                aws_secret_access_key=self.s3_skey,
                aws_access_key_id=self.s3_key) as client:

            # get list of objects for the bucket
            resp = await client.list_objects(Bucket=self.bucket)
            set_objects = {obj["Key"] for obj in resp['Contents']}

            # add all the objects inside the remote repo
            for obj in set_objects:
                # get object from s3
                response = await client.get_object(Bucket=self.bucket, Key=obj)

                # get the body
                async with response['Body'] as stream:
                    with tempfile.TemporaryFile() as tmp:
                        tmp.write(await stream.read())
                        tmp.seek(0)
                        dfinfo = tarobj.gettarinfo(fileobj=tmp, arcname=obj)
                        tarobj.addfile(dfinfo, tmp)

            # add an empty requirements.txt
            # in case is not included
            # to prevent pip install from fail
            if "requirements.txt" not in set_objects:
                file = b"# requirements file\n"
                file_info = tarfile.TarInfo("requirements.txt")
                file_info.size = len(file)
                tarobj.addfile(file_info, io.BytesIO(file))

            # add dockerfile
            docker_file = docker_string.format(
                image=self.base_image).encode("utf-8")
            docker_file_info = tarfile.TarInfo("Dockerfile")
            docker_file_info.size = len(docker_file)
            tarobj.addfile(docker_file_info, io.BytesIO(docker_file))

            # close the tar object
            tarobj.close()

            self.tar_tempfile.seek(0)
            return self.tar_tempfile

    async def __aexit__(self, exc_type, exc, tb):
        """Close the tempfile."""
        self.tar_tempfile.close()
        log.info(f"File {self.file_path} removed.")
