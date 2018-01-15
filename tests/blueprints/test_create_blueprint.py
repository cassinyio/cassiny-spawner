# create blueprint from file
import io
import tarfile

from blueprints.build_from_file import CreateFromFile


def test_build_from_file():
    path = "test.tar.gz"
    with tarfile.open(path, "w:gz") as fp:
        file = b"print('Hello')\n"
        file_info = tarfile.TarInfo("code.py")
        file_info.size = len(file)
        fp.addfile(file_info, io.BytesIO(file))
    with CreateFromFile(file_path=path, base_image="python") as fp:
        with tarfile.open(fileobj=fp, mode="r") as inner_fp:
            files = inner_fp.getnames()
            assert "Dockerfile" in files
            assert "requirements.txt" in files
            assert "code.py" in files
