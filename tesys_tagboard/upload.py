from typing import TYPE_CHECKING

import magic

if TYPE_CHECKING:
    from pathlib import Path

    from django.core.files.uploadedfile import UploadedFile


def get_file_content_type(file: Path):
    return magic.from_buffer(file.open("rb").read(2048), mime=True)


def fix_upload_content_type(file: UploadedFile):
    # Correct content-type based on file signature if necessary
    file.content_type = magic.from_buffer(file.open("rb").read(2048), mime=True)
    return file
