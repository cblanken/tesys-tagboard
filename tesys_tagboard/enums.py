from dataclasses import dataclass
from enum import Enum
from enum import IntEnum
from enum import StrEnum
from typing import Self


class RatingLevel(IntEnum):
    """Rating levels for posts
    Default: UNRATED

    These levels are ordered such that SAFE < UNRATED < QUESTIONABLE < EXPLICIT
    This enables a simple integer comparison to be made on the RatingLevel value
    to show only the desired posts
    """

    SAFE = 0
    UNRATED = 1
    QUESTIONABLE = 50
    EXPLICIT = 100

    @classmethod
    def choices(cls):
        return [(level.value, level.name) for level in cls]

    @classmethod
    def select(cls, name: str) -> RatingLevel | None:
        """Select rating level by label

        Lettercase is ignored
        """
        name = name.strip()
        selected_ratings = [r for r in RatingLevel if r.name.lower() == name.lower()]
        if len(selected_ratings) == 0:
            msg = f'Not match for rating level called "{name}"'
            raise ValueError(msg)
        return selected_ratings[0]


class MediaCategory(StrEnum):
    """MIME media content type"""

    AUDIO = "audio"
    IMAGE = "image"
    VIDEO = "video"


@dataclass
class MediaType:
    """A class describing the content type of some media following
    the MIME data convention
    desc: a string describing the MediaType
    extensions: a list of valid file extension for the MediaType
    category: a MediaCategory (AUDIO, IMAGE, or VIDEO)
    subtype: a Media's subtype (e.g. 'svg' in image/svg, or 'png' in image/png)
    suffix: an optional suffix to the MediaType definition (e.g. 'xml' in image/svg+xml)
    """

    desc: str
    extensions: list[str]
    category: MediaCategory
    subtype: str
    suffix: str = ""

    def get_template(self):
        template = f"{self.category.value}/{self.subtype}"
        if self.suffix:
            template += f"+{self.suffix}"
        return template


class SupportedMediaTypes(Enum):
    # Image types
    AVIF = MediaType("AVIF image", ["avif"], MediaCategory.IMAGE, "avif")
    BMP = MediaType("Windows Bitmap Graphics", ["bmp"], MediaCategory.IMAGE, "bmp")
    GIF = MediaType("GIF", ["gif"], MediaCategory.IMAGE, "gif")
    JPEG = MediaType("JPEG image", ["jpg", "jpeg"], MediaCategory.IMAGE, "jpeg")
    PNG = MediaType("PNG", ["png"], MediaCategory.IMAGE, "png")
    WEBP = MediaType("WEBP image", ["webp"], MediaCategory.IMAGE, "webp")
    TIFF = MediaType("TIFF image", ["tif", "tiff"], MediaCategory.IMAGE, "tiff")
    # TODO: support SVG

    # Audio types
    MP3 = MediaType("MP3 audio", ["mp3", "mpeg"], MediaCategory.AUDIO, "mpeg")
    WAV = MediaType("WAV audio", ["wav"], MediaCategory.AUDIO, "vnd.wav")
    WAV2 = MediaType("WAV audio", ["wav"], MediaCategory.AUDIO, "vnd.wave")
    WAV3 = MediaType("WAV audio", ["wav"], MediaCategory.AUDIO, "wave")

    # Video types
    MP4 = MediaType("MP4 video", ["mp4"], MediaCategory.VIDEO, "mp4")
    MPEG = MediaType("MPEG video", ["mpeg"], MediaCategory.VIDEO, "mpeg")
    WEBM = MediaType("WEBM video", ["webm"], MediaCategory.VIDEO, "webm")

    @classmethod
    def find(cls, template: str) -> Self | None:
        """A function to search the supported media types by
        template string.
        Returns the first matched instance of SupportedMediaTypes"""
        for smt in cls:
            if template == smt.value.get_template():
                return smt

        return None
