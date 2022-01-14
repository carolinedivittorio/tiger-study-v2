class Course:
    def __init__(self, info):
        self._class_dept = info[0]
        self._class_num = info[1]
        self._endorsed = info[2]
        self._title = info[3]
        self._notes = info[4]

    def getDept(self):
        return self._class_dept

    def getNum(self):
        return self._class_num

    # 0 --> prof has said hard no
    # 1 --> prof has not responded
    # 2 --> prof has given ok
    def isEndorsed(self):
        return self._endorsed

    def getTitle(self):
        return self._title

    def getNotes(self):
        return self._notes
