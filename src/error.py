__all__ = ["NoResultsError"]


class NoResultsError(Exception):

    def __init__(self, message="No results found."):
        self.message = message
        super().__init__(self.message)
