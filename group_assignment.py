class GroupAssignment:
    def __init__(self, info):
        self._groupid = info[0]
        self._netid = info[1]

    def getGroupId(self):
        return self._groupid

    def getNetid(self):
        return self._netid
