class Cycle:
    def __init__(self, info):
        self._netid = info[0]
        self._start = info[1]
        self._term = info[2]

    def getNetid(self):
        return self._netid

    def getStart(self):
        return str(self._start)

    def getTerm(self):
        return self._term

    def getSemester(self):
        # 1220 = spring 21 diff = 0
        # 1221 = summer 21 diff = 1
        # 1222 = fall 21 diff = 2
        # 1223 = spring 22 diff = 3
        # 1224 = summer 22 diff = 4
        # 1225 = fall 22 diff = 5
        # 1226 = spring 23 diff = 6
        diff = int(self._term) - 1220
        year = int(diff / 3) + 2021
        sem = diff % 3
        if sem == 0:
            sem_name = 'Spring '
        elif sem == 1:
            sem_name = 'Summer '
        elif sem == 2:
            sem_name = 'Fall '
        
        return sem_name + str(year)

   

