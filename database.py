#!/usr/bin/env python

# ---------------------------------------------------------------------
# database.py
# Author: Caroline di Vittorio '22
# ---------------------------------------------------------------------

from sqlalchemy import *

from student import Student
from alert import Alert
from course import Course
from group_assignment import GroupAssignment
from study_groups import StudyGroup
from scraper import scrape
from datetime import date
from cycle import Cycle

GROUP_NO_STUDENTS_MIN = 3
GROUP_NO_STUDENTS_MAX = 6

# ------ DATABASE CONFIGURATION -------
# ---------------------------------------------------------------------
db_string = "postgresql://ckawtmgwbbedeh:9fa105b5e1777f0cd9778e25571aa93741e9b40b75cc517d80eef29523463eb0@ec2-34-" \
            "203-255-149.compute-1.amazonaws.com:5432/d33o6p8hneg4ca"

db = create_engine(db_string)
meta = MetaData()

# ---------------------------------------------------------------------
student = Table(
    'student', meta,
    Column('netid', String, primary_key=True),
    Column('first_name', String),
    Column('last_name', String),
    Column('phone', String),
    Column('availability', String),
    Column('honor_code', String),
)

group_info = Table(
    'group_info', meta,
    Column('groupid', Integer, primary_key=True),
    Column('dept', String),
    Column('classnum', String),
)

group_assignment = Table(
    'group_assignment', meta,
    Column('groupid', Integer, primary_key=True),
    Column('netid', String),
)

classes = Table(
    'classes', meta,
    Column('dept', String),
    Column('classnum', String),
    Column('endorsed', Integer),
    Column('title', String),
    Column('notes', String),
)

admin = Table(
    'admin', meta,
    Column('netid', String),
)

faculty_access = Table(
    'faculty_access', meta,
    Column('netid', String),
)

cycle = Table(
    'cycle', meta,
    Column('netid', String),
    Column('start', Date),
    Column('term', String),
)


# ---------------------------------------------------------------------
# --------------------- DATABASE INTERFACE ----------------------------
# ---------------------------------------------------------------------

# ---------------------------------------------------------------------
# --- CYCLE ----
def getCycleInfo():
    conn = db.connect()
    stmt = cycle.select()
    result = conn.execute(stmt)
    conn.close()
    return Cycle(result.fetchone())

# ---------------------------------------------------------------------
# --- ADMIN ----
# returns true if the relevant netid is granted admin access
def isAdmin(netid):
    conn = db.connect()
    stmt = admin.select().where(admin.c.netid == netid)
    result = conn.execute(stmt)
    conn.close()
    return result.fetchone() is not None

# adds relevant netid to authorized admin access
def addAdmin(netid):
    if netid is None or netid == "":
        return Alert(["danger", "Enter an admin netid."])
    if isAdmin(netid):
        return Alert(["danger", str(netid) + " is already an admin."])
    conn = db.connect()
    stmt = admin.insert().values(netid=netid)
    conn.execute(stmt)
    conn.close()
    return Alert(["success", str(netid) + " added successfully!"])

# removes relevant netid from authorized admin access
def deleteAdmin(netid):
    if netid == '':
        return Alert(["danger", "Enter an admin netid."])
    if isAdmin(netid):
        conn = db.connect()
        stmt = admin.delete().where(admin.c.netid == netid)
        conn.execute(stmt)
        conn.close()
        return Alert(["success", str(netid) + " removed successfully!"])
    return Alert(["danger", str(netid) + " not an admin."])

# returns a list of netids of all authorized admin
def getAdmin():
    conn = db.connect()
    stmt = admin.select()
    result = conn.execute(stmt)
    conn.close()
    admins = []
    for row in result:
        admins.append(row[0])
    return admins


# ---------------------------------------------------------------------
# --- FACULTY ----
# return true if the relevant netid has faculty access
def isFaculty(netid):
    conn = db.connect()
    stmt = faculty_access.select().where(faculty_access.c.netid == netid)
    result = conn.execute(stmt)
    conn.close()
    return result.fetchone() is not None

# adds relevant netid to authorized faculty list
def addFaculty(netid):
    if netid is None or netid == "":
        return Alert(["danger", "Enter a faculty netid."]) 
    if isFaculty(netid):
        return Alert(["danger", str(netid) + " is already an approved faculty."])
    conn = db.connect()
    stmt = faculty_access.insert().values(netid=netid)
    conn.execute(stmt)
    conn.close()
    return Alert(["success", str(netid) + " added successfully!"])

# removes relevant netid from authorized faculty access
def deleteFaculty(netid):
    if netid == '':
        return Alert(["danger", "Enter a faculty netid."])
    if isFaculty(netid):
        conn = db.connect()
        stmt = faculty_access.delete().where(faculty_access.c.netid == netid)
        conn.execute(stmt)
        conn.close()
        return Alert(["success", str(netid) + " removed successfully!"])
    return Alert(["danger", str(netid) + " not an approved faculty."])

# returns a list of netids of all authorized faculty
def getFaculty():
    conn = db.connect()
    stmt = faculty_access.select()
    result = conn.execute(stmt)
    conn.close()
    faculty = []
    for row in result:
        faculty.append(row[0])
    return faculty


# ---------------------------------------------------------------------
# --- STUDENT ----
# creates a new student in database
def createNewStudent(netid):
    conn = db.connect()
    stmt = student.insert().values(netid=netid, availability='{True, True, True, True, True, True, True}',
                                   honor_code='not accepted')
    conn.execute(stmt)
    conn.close()

# returns a student object with the relevant student information
def getStudentInformation(netid):
    conn = db.connect()
    stmt = student.select().where(student.c.netid == netid)
    result = conn.execute(stmt)
    info = result.fetchone()
    conn.close()
    return None if info is None else Student(info)

# student_info is a Student object
# updates the relevant student with the information in student_info
def updateStudent(student_info):
    if student_info is None or student_info.getNetid == "":
        return Alert(['failure', "Please Enter Contact Information"])
    conn = db.connect()
    stmt = student.delete().where(student.c.netid == student_info.getNetid())
    conn.execute(stmt)
    stmt = student.insert().values(netid=student_info.getNetid(), first_name=student_info.getFirstName(),
                                   last_name=student_info.getLastName(), phone=student_info.getPhone(),
                                   availability=student_info.getAvailability(), honor_code=student_info.getHonorCode())
    conn.execute(stmt)
    conn.close()
    return Alert(['success', "Your contact information has been successfully saved."])

# returns true if this is the first login of a student, and false otherwise
def firstLogin(netid):
    return getStudentInformation(netid) is None


# ---------------------------------------------------------------------
# --- COURSES ----
# returns the title of the class
def getCourseTitle(dept, num):
    conn = db.connect()
    stmt = classes.select().where(classes.c.dept == dept).where(classes.c.classnum == str(num))
    result = conn.execute(stmt)
    title = Course(result.fetchone()).getTitle()
    conn.close()
    return title

# returns the number of groups in that class
def numberGroupsInClass(dept, num):
    conn = db.connect()
    stmt = group_info.select().where(group_info.c.dept == dept).where(group_info.c.classnum == num)
    result = conn.execute(stmt)
    conn.close()
    return len(result.fetchall())

# returns a list of netids of the students in the relevant group
def getStudentsInGroup(groupid):
    conn = db.connect()
    stmt = group_assignment.select().where(group_assignment.c.groupid == groupid)
    result = conn.execute(stmt)
    netids = []
    for row in result:
        netids.append(GroupAssignment(row).getNetid())
    conn.close()
    return netids

# returns a list of netids of the students in the relevant class
def getStudentsInClass(dept, num):
    conn = db.connect()
    stmt = group_assignment.select().where(group_assignment.c.groupid == group_info.c.groupid).where(
        group_info.c.dept == dept).where(group_info.c.classnum == num)
    result = conn.execute(stmt)
    netids = []
    for row in result:
        netids.append(GroupAssignment(row).getNetid())
    conn.close()
    return netids

# returns true if the student is already joined in the class
def isStudentInClass(netid, dept, num):
    global group_assignment
    global group_info
    conn = db.connect()
    stmt = group_assignment.select().where(group_assignment.c.netid == netid).where(
        group_assignment.c.groupid == group_info.c.groupid).where(group_info.c.dept == dept).where(
        group_info.c.classnum == num)
    result = conn.execute(stmt)
    conn.close()
    return result.fetchone() is not None

# gets the relevant class from database
def getCourse(dept, num):
    conn = db.connect()
    stmt = classes.select().where(classes.c.dept == dept).where(classes.c.classnum == num)
    result = conn.execute(stmt)
    for row in result:
        return Course(row)
    return None

# returns the endorsement status of the relevant class 
def getClassEndorsement(dept, coursenum):
    conn = db.connect()
    stmt = classes.select().where(classes.c.classnum == coursenum).where(classes.c.dept == dept)
    result = conn.execute(stmt)
    return Course(result.fetchone()).isEndorsed()

# returns the groupids that the relevant student has joined (both approved and unapproved)
def getJoinedGroups(netid):
    conn = db.connect()
    stmt = group_assignment.select().where(group_assignment.c.netid == netid).where(
        group_assignment.c.groupid == group_info.c.groupid).order_by(group_info.c.dept, group_info.c.classnum)
    result = conn.execute(stmt)
    groups = []
    for row in result:
        groups.append(row[0])
    conn.close()
    return groups

# returns the classes that the relevant student has joined (both approved and unapproved)
def getJoinedClasses(netid):
    conn = db.connect()
    stmt = group_info.select().where(group_assignment.c.netid == netid).where(
        group_assignment.c.groupid == group_info.c.groupid).order_by(group_info.c.dept, group_info.c.classnum)
    result = conn.execute(stmt)
    courses = []
    for row in result:
        courses.append([row[1], row[2]])
    conn.close()
    return courses

# returns the group that the relevant student has been assigned to in that class
def getGroupOfStudentInClass(netid, dept, num):
    conn = db.connect()
    stmt = group_info.select().where(group_assignment.c.netid == netid)\
        .where(group_assignment.c.groupid == group_info.c.groupid)\
        .where(group_info.c.dept == dept)\
        .where(group_info.c.classnum==num)
    result = conn.execute(stmt)
    return result.fetchone()[0]

# creates a new group within the relevant class; returns the groupid
def createNewGroup(dept, classnum):
    global group_info
    global classes
    conn = db.connect()
    stmt = group_info.insert().values(dept=dept, classnum=classnum)
    result = conn.execute(stmt)
    key = result.inserted_primary_key[0]
    conn.close()
    return key

# returns the number of students in the relevant group
def getNumStudentsInGroup(groupid):
    conn = db.connect()
    stmt = group_assignment.select().where(group_assignment.c.groupid == groupid)
    result = conn.execute(stmt)
    conn.close()
    return len(result.fetchall())

# returns the number of groups in the relevant class
def getNumGroupsInClass(dept, num):
    conn = db.connect()
    stmt = group_info.select().where(group_info.c.dept == dept).where(group_info.c.classnum == num)
    result = conn.execute(stmt)
    conn.close()
    return len(result.fetchall())

# returns the number of students in the class
def getNumStudentsInClass(dept, num):
    conn = db.connect()
    stmt = group_assignment.select()\
        .where(group_info.c.dept == dept)\
        .where(group_info.c.classnum == num)\
        .where(group_info.c.groupid == group_assignment.c.groupid)

    result = conn.execute(stmt)
    conn.close()
    return len(result.fetchall())

# returns the groupid of all the approved course groups that have been joined by the student
def getPublicJoinedGroups(netid):
    conn = db.connect()
    stmt = group_assignment.select()\
        .where(group_assignment.c.netid == netid)\
        .where(group_assignment.c.groupid == group_info.c.groupid)\
        .where(group_info.c.dept == classes.c.dept)\
        .where(group_info.c.classnum == classes.c.classnum)\
        .where(classes.c.endorsed == 2)\
        .order_by(group_info.c.dept, group_info.c.classnum)

    result = conn.execute(stmt)
    groups = []
    for row in result:
        groups.append(row[0])
    conn.close()
    return groups

# returns the study group information for the relevant groupid
def getGroupInformation(groupid):
    conn = db.connect()
    stmt = group_info.select().where(group_info.c.groupid == groupid)
    result = conn.execute(stmt).fetchone()
    conn.close()
    if result is not None:
        return StudyGroup(result)
    else:
        return None

# returns a list of groups in class
def getGroupsInClass(dept, num):
    groups = []
    conn = db.connect()
    stmt = group_info.select().where(group_info.c.dept == dept).where(group_info.c.classnum == num)
    result = conn.execute(stmt)
    for row in result:
        group = StudyGroup(row)
        groups.append(group)
    conn.close()
    return groups


# ---------------------------------------------------------------------
# APPLICATION FUNCTIONS
# ---------------------------------------------------------------------
# search the database for classes
# class_dept or class_num == "" means search all of the classes
def search(class_dept, class_num):
    conn = db.connect()
    stmt = classes.select() \
        .where(classes.c.classnum.like("%" + str(class_num) + "%")) \
        .where(classes.c.dept.like("%" + str(class_dept.upper()) + "%"))

    result = conn.execute(stmt.order_by(classes.c.dept, classes.c.classnum))

    returned_classes = []
    if result is not None:
        for row in result:
            returned_classes.append(Course(row))
    return returned_classes

def searchStudents(netid):
    conn = db.connect()
    stmt = student.select() \
        .where(student.c.netid.like("%" + str(netid) + "%"))\
        
    result = conn.execute(stmt.order_by(student.c.netid))

    returned_students = []
    if result is not None:
        for row in result:
            returned_students.append(Student(row))
    return returned_students


# -------------------------------------------------------------
# have student with netid join the class with dept, num
def addStudentToClass(netid, dept, num):
    if isStudentInClass(netid, dept, num):
        return Alert(["failed", "student already in class"])

    endorsement_status = getClassEndorsement(dept, num)
    if endorsement_status == 0:
        return Alert(["failed", "class has been denied"])

    # check if there exists a group to add to
    groups = getGroupsInClass(dept, num)
    for group in groups:
        if getNumStudentsInGroup(group.getGroupId()) < GROUP_NO_STUDENTS_MAX:
            addStudentToGroup(netid, group.getGroupId())
            return Alert(["success", group.getGroupId()])

    # create new group if necessary
    new_groupid = createNewGroup(dept, num)
    addStudentToGroup(netid, new_groupid)
    return Alert(["success", new_groupid])        

# adds the student defined by netid to the group with groupid
def addStudentToGroup(netid, groupid):
    if netid in getStudentsInGroup(groupid):
        return
    conn = db.connect()
    stmt = group_assignment.insert().values(groupid=groupid, netid=netid)
    conn.execute(stmt)
    conn.close()


# -----------------------------------------------------------------------
# removes the student with netid from the relevant group (and therefore class)
def removeStudentFromGroup(netid, groupid, dept, num):
    if netid is None:
        return
    if groupid is None:
        return
    if isStudentInClass(netid, dept, num):
        conn = db.connect()
        stmt = group_assignment.delete().where(group_assignment.c.groupid == groupid).where(
            group_assignment.c.netid == netid)
        conn.execute(stmt)
        if getNumStudentsInGroup(groupid) <= 0:
            stmt = group_info.delete().where(group_info.c.groupid == groupid)
            conn.execute(stmt)
        conn.close()


# -----------------------------------------------------------------------
# switches the student with netid into a new group for the class defined
# by dept/num
def switchGroup(netid, dept, num):
    if not isStudentInClass(netid, dept, num):
        return Alert(["failed", "student not in class"])

    endorsement_status = getClassEndorsement(dept, num)
    if endorsement_status == 0:
        return Alert(["failed", "class has been denied"])

    # get current groupid
    conn = db.connect()
    stmt = group_assignment.select().where(group_info.c.dept == dept).where(group_info.c.classnum == num).where(
        group_assignment.c.groupid == group_info.c.groupid).where(group_assignment.c.netid == netid)
    result = conn.execute(stmt)
    curr_groupid = -1
    for row in result:
        curr_groupid = row[0]

    removeStudentFromGroup(netid, curr_groupid, dept, num)
    # check if there exists a group to add to
    groups = getGroupsInClass(dept, num)
    for group in groups:
        if getNumStudentsInGroup(group.getGroupId()) < GROUP_NO_STUDENTS_MAX and group.getGroupId() != curr_groupid:
            addStudentToGroup(netid, group.getGroupId())
            return Alert(["success", group.getGroupId()])

    # create new group if necessary
    new_groupid = createNewGroup(dept, num)
    addStudentToGroup(netid, new_groupid)
    return Alert(["success", new_groupid]) 



# -----------------------------------------------------------------------
def approveCourse(dept, num, approval, msg):
    conn = db.connect()
    stmt = classes.select().where(classes.c.dept == dept).where(classes.c.classnum == num)
    result = conn.execute(stmt)
    course = Course(result.fetchone())

    stmt = classes.update()\
        .values(endorsed=approval, notes=msg)\
        .where(classes.c.dept == dept)\
        .where(classes.c.classnum == num)
    conn.execute(stmt)
    conn.close()

    if approval == 0:
        if course.isEndorsed() == 0:
            return None
        if getNumGroupsInClass(dept, num) > 0:
            netids = getStudentsInClass(dept, num)
            return [0, netids]

    if approval == 2:
        if course.isEndorsed() == 2:
            return None
        if getNumGroupsInClass(dept, num) > 0:
            groupids = getGroupsInClass(dept, num)
            all_groups = []
            for id in groupids:
                all_groups.append(getStudentsInGroup(id.getGroupId()))
            return [2, all_groups]

    return None

# -----------------------------------------------------------------------
# OTHER ADMIN
# -----------------------------------------------------------------------
# gathers the breakdwon information for the admin page
def getAdminBreakdown():
    conn = db.connect()
    stmt = student.select()
    result = conn.execute(stmt).fetchall()
    num_student_visisted = 0 if result is None else len(result)

    stmt = group_info.select()
    result = conn.execute(stmt).fetchall()
    num_groups = 0 if result is None else len(result)

    stmt = group_assignment.select()
    result = conn.execute(stmt).fetchall()
    num_participants = 0 if result is None else len(result)

    conn.close()
    return [num_student_visisted, num_groups, num_participants]

# -----------------------------------------------------------------------
# ADMIN RESET
# -----------------------------------------------------------------------
# inserts new class into the database. Used when the database is being reset.
def instantiateClass(dept, num, title):
    conn = db.connect()
    stmt = classes.insert().values(dept=dept, classnum=num, title=title, endorsed=1, notes="")
    conn.execute(stmt)
    conn.close()


# -----------------------------------------------------------------------
# Resets the database for new use. Deletes all information within it and reloads
# all current class information.
# USE WITH TREMENDOUS CAUTION
def reset_classes(netid):
    conn = db.connect()
    stmt = classes.delete()
    # conn.execute(stmt)
    # stmt = group_assignment.delete()
    # conn.execute(stmt)
    # stmt = group_info.delete()
    # conn.execute(stmt)
    # stmt = student.delete()
    # conn.execute(stmt)
    stmt = cycle.delete()
    conn.execute(stmt)    

    #start a new cycle
    stmt = cycle.insert().values(netid=netid, start=date.today(), term=str(term))
    conn.execute(stmt)
    conn.close()
    #set the classes
    DEPTS = ["AAS", "AFS", "AMS", "ANT", "AOS", "APC", "ARA", "ARC", "ART", "ASA", "AST", "ATL", "BCS", 
        "CBE", "CEE", "CGS", "CHI", "CHM", "CHV", "CLA", "CLG", "COM", "COS", "CWR", "CZE", "DAN", "EAS", 
        "ECO", "ECS", "EEB", "EGR", "ELE", "ENE", "ENG", "ENT", "ENV", "EPS", "FIN", "FRE", "FRS", "GEO", 
        "GER", "GHP", "GSS", "HEB", "HIN", "HIS", "HLS", "HOS", "HUM", "ISC", "ITA", "JDS", "JPN", "JRN", 
        "KOR", "LAO", "LAS", "LAT", "LIN", "MAE", "MAT", "MED", "MOD", "MOG", "MOL", "MPP", "MSE", "MTD", 
        "MUS", "NES", "NEU", "ORF", "PAW", "PER", "PHI", "PHY", "POL", "POP", "POR", "PSY", "QCB", "REL", 
        "RES", "RUS", "SAN", "SAS", "SLA", "SML", "SOC", "SPA", "SPI", "STC", "SWA", "THR", "TPP", "TRA", 
        "TUR", "TWI", "URB", "URD", "VIS", "WRI"]
    num_courses = 0
    for dept in DEPTS:
        scrape_results = scrape(dept)
        print('scraped ' + str(dept))
        for course in scrape_results:
            num_courses = num_courses + 1
            coursenum = course.get("coursenum")
            title = course.get("title")
            if coursenum[0].isnumeric() and int(coursenum[0]) < 6:
                instantiateClass(dept, coursenum, title)
    print(num_courses)



def testing():
    conn = db.connect()
    stmt = cycle.insert().values(netid='cmdv', start=date.today(), term='1223')
    conn.execute(stmt)
    conn.close()

# ---------------------------------------------------------------------
if __name__ == '__main__':
    print('database.py')
    testing()


