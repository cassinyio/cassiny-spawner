import io
import os
import tarfile
import tempfile

import aiobotocore
from jinja2 import Environment, FileSystemLoader

# Capture our current directory
PATH = os.path.dirname(os.path.abspath(__file__))
j2_env = Environment(loader=FileSystemLoader(PATH), trim_blocks=True)


class MakeTarFromFo:
    """
    Context manager to build a docker images from a cargo (minio bucket).

    """

    def __init__(
        self,
        cargo: str,
        s3_key: str,
        s3_skey: str,
        image: str,
        bucket: str="default"
    ) -> None:
        self.bucket = bucket
        self.s3_key = s3_key
        self.s3_skey = s3_skey
        self.cargo = 'http://cargo-raspyheka-9904.cssny.space'  # TODO REMOVE THIS
        self.image = image

    async def __aenter__(self):
        session = aiobotocore.get_session()

        self.tar_tempfile = tempfile.TemporaryFile()
        tar_obj = tarfile.open(mode='w:gz', fileobj=self.tar_tempfile)

        async with session.create_client(
                's3', use_ssl=False,
                endpoint_url=self.cargo,
                aws_secret_access_key=self.s3_skey,
                aws_access_key_id=self.s3_key) as client:

            # get list of objects for the bucket
            resp = await client.list_objects(Bucket=self.bucket)
            set_objects = {obj["Key"] for obj in resp['Contents']}

            for obj in set_objects:
                # get object from s3
                response = await client.get_object(Bucket=self.bucket, Key=obj)

                # get the body
                async with response['Body'] as stream:
                    with tempfile.TemporaryFile() as tmp:
                        tmp.write(await stream.read())
                        tmp.seek(0)
                        dfinfo = tar_obj.gettarinfo(fileobj=tmp, arcname=obj)
                        tar_obj.addfile(dfinfo, tmp)

            # add am empty requirements.txt
            # in case is not included
            # to prevent pip install to fail
            if "requirements.txt" not in set_objects:
                with tempfile.TemporaryFile() as tmp:
                    tmp.write(b"# requirements file\n")
                    tmp.seek(0)
                    dfinfo = tar_obj.gettarinfo(
                        fileobj=tmp, arcname="requirements.txt")
                    tar_obj.addfile(dfinfo, tmp)

            self.render_template(
                "Dockerfile",
                tar=tar_obj,
                image=self.image
            )

            with open(os.path.join(PATH, "app.py"), mode="rb") as f:
                dfinfo = tar_obj.gettarinfo(fileobj=f, arcname="app.py")
                tar_obj.addfile(dfinfo, f)

            # close the tar object
            tar_obj.close()

            self.tar_tempfile.seek(0)
            return self.tar_tempfile

    async def __aexit__(self, exc_type, exc, tb):
        self.tar_tempfile.close()

    @staticmethod
    def render_template(name, tar, **kwargs):
        template = j2_env.get_template(name)\
            .render(**kwargs).encode('utf-8')
        try:
            output = io.BytesIO(template)
            tarinfo = tarfile.TarInfo(name)
            tarinfo.size = len(template)
            tar.addfile(tarinfo, output)
        finally:
            output.close()
