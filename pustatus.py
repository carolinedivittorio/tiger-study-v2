import ldap3


# ServerConnection object used to hold login credentials for the ldap server
# This should ideally be created using a service account but can be used with
# any valid Princeton Netid and password
class ServerConnection:
    def __init__(self, username, password):
        self.username = username
        self.password = password


# Completes the ldap server query using a ServerConnection serverconnection, a
# Netid netid whose attribute att you want to check If the uid has the att
# queried, serversearch will return True, otherwise False
def __serversearch(serverconnection, netid, att):
    username = serverconnection.username;
    password = serverconnection.password;
    server = ldap3.Server('ldap.princeton.edu', 636, use_ssl=True)
    connect = ldap3.Connection(server, "uid=" + username +
                               ",o=princeton university,c=us", password)
    connect.bind()
    result = connect.search("o=princeton university,c=us",
                            "(&(uid=" + netid + ")(pustatus=" + att + "))")
    return result


# queries the ldap server using the ServerConnection serverconnection object
# Checks to see if Netid netid has the attribute fac
# Returns True if they are a faculty member, otherwise false
def isFaculty(serverconnection, netid):
    return __serversearch(serverconnection, netid, "fac")


# queries the ldap server using the ServerConnection serverconnection object
# Checks to see if Netid has the attribute u*
# Returns True if they are an undergraduate student, otherwise false
def isUndergraduate(serverconnection, netid):
    return __serversearch(serverconnection, netid, "u*")


# queries the ldap server using the ServerConnection serverconnection object
# Checks to see if Netid netid has the attribute g*
# Returns True if they are a graduate student, otherwise false
def isGraduateStudent(serverconnection, netid):
    return __serversearch(serverconnection, netid, "g*")
