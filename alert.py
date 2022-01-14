class Alert:
    def __init__(self, data):
        self._type = data[0]
        self._message = data[1]

    def getType(self):
        return self._type

    def getMessage(self):
        return self._message
