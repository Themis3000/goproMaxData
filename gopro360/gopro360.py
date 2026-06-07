class GoPro360File:
    def __init__(self, file_path):
        self.f = open(file_path, "rb")

    def __repr__(self):
        return "test data"
