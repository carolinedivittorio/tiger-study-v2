from flask_login import UserMixin

class userAccount(UserMixin):

    def __init__(self, username, role):
        self.id = username
        self.role = role

    def getRole(self):
        return self.role

