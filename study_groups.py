class StudyGroup:
    def __init__(self, info):
        self._groupid = info[0]
        self._class_dept = info[1]
        self._class_num = info[2]

    def getGroupId(self):
        return self._groupid

    def getClassDept(self):
        return self._class_dept

    def getClassNum(self):
        return self._class_num





