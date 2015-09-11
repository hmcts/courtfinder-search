
class CourtSearchError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return self.value

class CourtSearchClientError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return self.value


class CourtSearchInvalidPostcode(CourtSearchError):
    pass