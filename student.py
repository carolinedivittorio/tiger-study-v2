class Student:
    def __init__(self, info):
        self._netid = info[0]
        self._first_name = info[1]
        self._last_name = info[2]
        self._phone = info[3]
        self._availability = info[4]
        self._honor_code = info[5]

    def getNetid(self):
        return self._netid

    def getFirstName(self):
        if self._first_name is None:
            return ""
        return self._first_name

    def getLastName(self):
        if self._last_name is None:
            return ""
        return self._last_name

    def getPhone(self):
        return self._phone

    def getAvailability(self):
        return self._availability

    def getHonorCode(self):
        return self._honor_code

    def print_student(self):
        print(str(self._netid) + ' ' + str(self._first_name) + ' ' + str(self._last_name) + ' ' +
              str(self._phone) + ' ' + str(self._availability))



