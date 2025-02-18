class ItHappensException(Exception):
    """Raise an error related to It Happens."""


class ItHappensImageNotFoundError(ItHappensException):
    """Raise when an image is not found."""

    def __init__(self, image, *args):
        self.image = image

    def __str__(self):
        return f'Image "{self.image}" was not found. If you are using the web app, did you upload them?'
