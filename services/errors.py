class AppError(Exception):
    """An error with an HTTP status code.

    Services raise this. main.py turns it into a JSON response like
    {"detail": "..."}, so services never need to know about HTTP.
    """

    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)
