# -----------------------------------------------------------------------
# emails.py
# Author: Caroline di Vittorio
# -----------------------------------------------------------------------
from flask_mail import Message
from database import *


# sends email to welcome new student to a new group when they are the first
# student in that group
def newGroupWelcomeEmail(netid, groupid):
    student_info = getStudentInformation(netid)
    first_name = netid if student_info.getFirstName() == "" else student_info.getFirstName()

    group_information = getGroupInformation(groupid)
    msg = Message(
        "Welcome to TigerStudy for " + str(group_information.getClassDept()) + str(group_information.getClassNum()),
        sender="tiger-study@princeton.edu",
        recipients=[netid + "@princeton.edu"])

    intro = "Dear " + str(first_name) + ", \n\nThank you for joining TigerStudy for " + str(
        group_information.getClassDept()) + str(group_information.getClassNum())
    msg.body = intro + ". You're the first member of your group! We will reach out to you very soon once we've " \
                       "matched you with other students. \n\nIn the meantime, for any questions or inquiries, feel " \
                       "free to respond to this email.\n\nKind regards,\n\nYour TigerStudy Friends "

    return msg


def courseDeniedEmail(netids, dept, num):
    emails = []
    for netid in netids:
        emails.append(str(netid) + "@princeton.edu")

    msg = Message(
        "Course Status Update for " + str(dept) + str(num),
        sender="tiger-study@princeton.edu",
        recipients=emails)

    msg.body = "Dear Student, \n\n We are so sorry, but your instructor has chosen to opt-out of using TigerStudy for this " \
               "course. As a result, we can't match you into any groups.\n\nKind regards, \n\nYour TigerStudy Friends "

    return msg


def courseApprovedEmail(groups, dept, num):
    for students in groups:
        contact_summary = ""
        email = []
        for std in students:
            s = getStudentInformation(std)
            email.append(s.getNetid() + "@princeton.edu")
            if s.getFirstName() != "":
                contact_summary += str(s.getFirstName()) + " " + str(s.getLastName()) + ": "
            contact_summary += str(s.getNetid()) + "@princeton.edu\n"

        msg = Message(dept + " " + num + " has been approved on TigerStudy",
                      sender="tiger-study@princeton.edu",
                      recipients=email)
        msg.body = "Hello TigerStudy Friends, \n\nJust wanted to let you know that " + \
                   str(dept) + " " + str(num) + " has been approved on TigerStudy. \n\nBelow is the " + \
                   "contact information of everyone in your group - and we will continue to reach out to you if others " \
                   "join " \
                   "in the future. Have fun!\n\n" + str(contact_summary)

    return msg


# -----------------------------------------------------------------------
# sends email welcome a new student to an already existing study group
def newStudentWelcomeEmail(netid, students, groupid):
    print('SENDING EMAIL IN NEW STUDENT WELCOME EMAIL')
    print(students)
    student_info = getStudentInformation(students[0])
    if student_info.getFirstName() == "":
        student_name = student_info.getNetid()
    else:
        student_name = str(student_info.getFirstName()) + " " + str(student_info.getLastName())
    netid = student_info.getNetid()
    group_information = getGroupInformation(groupid)
    email = [netid + "@princeton.edu"]
    contact_summary = ""
    for std in students:
        s = getStudentInformation(std)
        email.append(s.getNetid() + "@princeton.edu")
        if s.getFirstName() != "":
            contact_summary += str(s.getFirstName()) + " " + str(s.getLastName()) + ": "
        contact_summary += str(s.getNetid()) + "@princeton.edu\n"

    if student_info.getFirstName() == "":
        name_msg = "A new student"
    else:
        name_msg = str(student_info.getFirstName()) + " " + str(student_info.getLastName())
    msg = Message(name_msg +
                  " has joined your group for " + str(group_information.getClassDept()) +
                  str(group_information.getClassNum()),
                  sender="tiger-study@princeton.edu",
                  recipients=email)
    msg.body = "Hello TigerStudy Friends, \n\nJust wanted to let you know that " + str(
        student_name) + " has joined your " \
                        "study group for " + \
               str(group_information.getClassDept()) + str(group_information.getClassNum()) + ". \n\nBelow is the " + \
               "contact information of everyone in your group - and we will continue to reach out to you if others " \
               "join " \
               "in the future. Have fun!\n\n" + str(contact_summary)

    return msg


# -----------------------------------------------------------------------
# sends welcome email for first login of new student
def welcomeEmail(netid):
    email = [str(netid) + "@princeton.edu"]
    msg = Message("Welcome to TigerStudy!",
                  sender="tiger-study@princeton.edu",
                  recipients=email)
    msg.body = "Welcome to TigerStudy! \n\nWe're so glad that you've joined our community, and we wanted to reach out " \
               " and say hello.\n\nIf you have any feedback, questions or concerns, feel free to respond to this email or " \
               "reach out to our two site " \
               "administrators Caroline di Vittorio '22 (cmdv@princeton.edu) and Kasey McFadden '22 " \
               "(kaseym@princeton.edu).\n\nKind regards,\n\nThe TigerStudy Community"

    return msg


def waitingApprovalEmail(dept, num, netid):
    print('pending approval')
    print(dept)
    print(num)
    print(netid)
    email = [str(netid) + "@princeton.edu"]
    msg = Message("Thank you for signing up for " + str(dept) + str(num) + "!",
                  sender="tiger-study@princeton.edu",
                  recipients=email)
    msg.body = "This class is still pending approval from your professor. We will reach out to you as soon as we " \
               "hear back from the course instructors. We appreciate your patience. "

    email_admins = ['gawonj@princeton.edu', 'iokkinga@princeton.edu']
    msg_admins = Message("Someone has requested to join TigerStudy for " + str(dept) + str(num),
                         sender="tiger-study@princeton.edu",
                         recipients=email_admins)
    msg_admins.body = (str(netid) + " has requested to join " + str(dept) + str(num) + " on TigerStudy.")

    return [msg, msg_admins]
