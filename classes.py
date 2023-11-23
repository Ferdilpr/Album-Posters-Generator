from PIL import Image

fonts_directory = "fonts/"


class Fonts:
    def __init__(self, name):
        self.directory = fonts_directory + name + "/"
        self.black = Font(self.directory + name + "-Black.ttf")
        self.extra_bold = Font(self.directory + name + "-ExtraBold.ttf")
        self.bold = Font(self.directory + name + "-Bold.ttf")
        self.semi_bold = Font(self.directory + name + "-SemiBold.ttf")
        self.medium = Font(self.directory + name + "-Medium.ttf")
        self.regular = Font(self.directory + name + "-Regular.ttf")
        self.light = Font(self.directory + name + "-Light.ttf")
        self.extra_light = Font(self.directory + name + "-ExtraLight.ttf")
        self.thin = Font(self.directory + name + "-Thin.ttf")
        self.italic = self.directory + name + "-Italic.ttf"


class Font(str):
    def italic(self):
        return self.removesuffix(".ttf") + "Italic.ttf"


class Setting(object):
    def __init__(
            self,
            background_blur_radius,
            poster_width_percentage,
            center_image_padding_sides_percentage,
            center_image_padding_top_percentage,
            background_darkness,
            default_album_name_font_size_percentage,
            default_artist_name_font_size_percentage,
            default_album_infos_font_size_percentage,
            resolution_multiplicator,
            center_image_shadow_blur,
            center_image_shadow_size_percentage,
            center_image_shadow_color,
            background_saturation,
            name=""

    ):
        self.name = name
        self.background_blur_radius = background_blur_radius
        self.poster_width_percentage = poster_width_percentage
        self.center_image_padding_sides_percentage = center_image_padding_sides_percentage
        self.center_image_padding_top_percentage = center_image_padding_top_percentage
        self.background_darkness = background_darkness
        self.default_album_name_font_size_percentage = default_album_name_font_size_percentage
        self.default_artist_name_font_size_percentage = default_artist_name_font_size_percentage
        self.default_album_infos_font_size_percentage = default_album_infos_font_size_percentage
        self.resolution_multiplicator = resolution_multiplicator
        self.center_image_shadow_blur = center_image_shadow_blur
        self.center_image_shadow_size_percentage = center_image_shadow_size_percentage
        self.center_image_shadow_color = center_image_shadow_color
        self.background_saturation = background_saturation

    def copy(self,
             background_blur_radius=None,
             poster_width_percentage=None,
             center_image_padding_sides_percentage=None,
             center_image_padding_top_percentage=None,
             background_darkness=None,
             default_album_name_font_size_percentage=None,
             default_artist_name_font_size_percentage=None,
             default_album_infos_font_size_percentage=None,
             resolution_multiplicator=None,
             center_image_shadow_blur=None,
             center_image_shadow_size_percentage=None,
             center_image_shadow_color=None,
             background_saturation=None,
             name="",
             ):
        copy = Setting(
            self.background_blur_radius,
            self.poster_width_percentage,
            self.center_image_padding_sides_percentage,
            self.center_image_padding_top_percentage,
            self.background_darkness,
            self.default_album_name_font_size_percentage,
            self.default_artist_name_font_size_percentage,
            self.default_album_infos_font_size_percentage,
            self.resolution_multiplicator,
            self.center_image_shadow_blur,
            self.center_image_shadow_size_percentage,
            self.center_image_shadow_color,
            self.background_saturation,
            self.name
        )

        if background_blur_radius is not None:
            copy.background_blur_radius = background_blur_radius
        if poster_width_percentage is not None:
            copy.poster_width_percentage = poster_width_percentage
        if center_image_padding_sides_percentage is not None:
            copy.center_image_padding_sides_percentage = center_image_padding_sides_percentage
        if center_image_padding_top_percentage is not None:
            copy.center_image_padding_top_percentage = center_image_padding_top_percentage
        if background_darkness is not None:
            copy.background_darkness = background_darkness
        if default_album_name_font_size_percentage is not None:
            copy.default_album_name_font_size_percentage = default_album_name_font_size_percentage
        if default_artist_name_font_size_percentage is not None:
            copy.default_artist_name_font_size_percentage = default_artist_name_font_size_percentage
        if default_album_infos_font_size_percentage is not None:
            copy.default_album_infos_font_size_percentage = default_album_infos_font_size_percentage
        if resolution_multiplicator is not None:
            copy.resolution_multiplicator = resolution_multiplicator
        if center_image_shadow_blur is not None:
            copy.center_image_shadow_blur = center_image_shadow_blur
        if center_image_shadow_size_percentage is not None:
            copy.center_image_shadow_size_percentage = center_image_shadow_size_percentage
        if center_image_shadow_color is not None:
            copy.center_image_shadow_color = center_image_shadow_color
        if background_saturation is not None:
            copy.background_saturation = background_saturation
        copy.name = name

        return copy


class Album:

    def __init__(self, _album_name="", _release_date="", _tracks_count_raw=0,
                 _tracks_count="", _duration_raw="", _duration="", _cover_link="",
                 _tracks=None, _artist_name="", _label=""):
        if _tracks is None:
            _tracks = []
        self.album_name = _album_name
        self.release_date = _release_date
        self.tracks_count_raw = _tracks_count_raw
        self.tracks_count = _tracks_count
        self.duration_raw = _duration_raw
        self.duration = _duration
        self.cover_link = _cover_link
        self.tracks = _tracks
        self.artist_name = _artist_name
        self.label = _label


class Track:
    def __init__(
            self,
            title: str,
            duration_raw: int,
            duration: str,
            explicit_lyrics: bool,
            artist_name: str,
            album_name: str,
            file_name: str,
            cover_link: str
    ):
        self.title = title
        self.duration_raw = duration_raw
        self.duration = duration
        self.explicit_lyrics = explicit_lyrics
        self.artist_name = artist_name
        self.album_name = album_name
        self.file_name = file_name
        self.cover_link = cover_link
        self.cover = Image.open(cover_link).convert("RGB")
