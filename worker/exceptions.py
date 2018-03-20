class ImportingError(Exception):
    pass


class ImportingHTTPError(ImportingError):
    pass


class ValidationError(ImportingError):
    pass


class ViewError(Exception):
    pass


class InvalidContentTypeError(ViewError):
    pass


class InvalidContentError(ViewError):
    pass


class InvalidTokenError(ViewError):
    pass
