# -----------------------------------------------------------------------
# app.py
# Authors: Caroline di Vittorio and Kasey McFadden
# -----------------------------------------------------------------------

from flask_mail import Mail, Message
from flask import Flask, request, make_response, render_template
from sys import argv
from CASClient import CASClient
from emails import *
from student import Student
from database import *
# from scraper import scrape
# from breakdown import Breakdown
from alert import Alert
import datetime
import os

import pustatus

from flask_login import login_user, logout_user, login_required, LoginManager, current_user
from userAccount import userAccount

# -----------------------------------------------------------------------

LOCAL = True
# LOCAL = False
NETID = '[netid]'
if LOCAL:
    NETID = 'cmdv'
TESTING = True

# -----------------------------------------------------------------------

login_manager = LoginManager()

app = Flask(__name__, template_folder='./templates')

login_manager.init_app(app)

login_manager.login_view = "/"

app.secret_key = 'super secret key'  # os.environ['SECRET_KEY']
cas = CASClient()

# ------------------------------------------------------------
# CONFIGURATION VARIABLES

if LOCAL:
    app.config.update(
        MAIL_USE_TLS=True,
        MAIL_USE_SSL=False,
        MAIL_SUPPRESS_SEND=False,
        MAIL_PORT=587,
        MAIL_SERVER="smtp.office365.com",
        MAIL_USERNAME="tiger-study@princeton.edu",
        MAIL_PASSWORD="RoarTogether123!",
    )

else:
    app.config.update(
        MAIL_USE_TLS=True,
        MAIL_USE_SSL=False,
        MAIL_SUPPRESS_SEND=False,
        MAIL_PORT=587,
        MAIL_SERVER=os.environ['MAIL_SERVER'],
        MAIL_USERNAME=os.environ['MAIL_USERNAME'],
        MAIL_PASSWORD=os.environ['MAIL_PASSWORD'],
    )

mail = Mail(app)

# ------------------------------------------------------------------------------
# SETS UP LOGIN SYSTEM
if LOCAL:
    ldapserver = pustatus.ServerConnection("tiger-study", "RoarTogether123!")
else:
    ldapserver = pustatus.ServerConnection(os.environ['LDAP_USERNAME'], os.environ['MAIL_PASSWORD'])


# returns special, undergraduates or other
def uservalidation(netid):
    special = isAdmin(netid)
    if special:
        return "special"
    undergrad = pustatus.isUndergraduate(ldapserver, netid)
    if undergrad:
        return "undergraduates"

    if isFaculty(netid):
        return "undergraduates"
    return "other"


# checks that the user's role matches the page type
def checkuser(role, pageType):
    if role == pageType:
        return True
    elif role == "special":
        return True
    else:
        return False


def loginfail():
    html = render_template('loginfail.html')
    response = make_response(html)
    return response


@login_manager.user_loader
def load_user(user_id):
    try:
        username = CASClient().authenticate()
        if user_id != username:
            return None
        role = uservalidation(user_id)
        return userAccount(user_id, role)
    except Exception as e:
        loginfail()


# -----------------------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------------------
# adds the student with the relevant netid to the class relevant class. If the student is assigned a study group
# where the student is the only member, sends a special email. Otherwise, send an email to the student and all
# others in the study group informing of the new student.
def _addStudentToClass(netid, class_dept, class_num):
    groupid = addStudentToClass(netid, class_dept, class_num)

    endorsement_status = getClassEndorsement(class_dept, class_num)

    if endorsement_status == 0:
        return

    if endorsement_status == 1:
        if not TESTING:
            mail.send(waitingApprovalEmail(class_dept, class_num, netid))
        return

    students_in_group = getStudentsInGroup(groupid)
    if (len(students_in_group <= 1)):
        if not TESTING:
            mail.send(newGroupWelcomeEmail(netid, groupid))
    else:
        if not TESTING:
            mail.send(newStudentWelcomeEmail(netid, students_in_group, groupid))

    return groupid


# ------------------------------------------------------------------------------
# STUDENT JOIN CLASS PORTAL
# ------------------------------------------------------------------------------
@app.route('/')
@app.route('/home')
def home():
    netid = NETID
    isFirstLogin = True
    if not LOCAL:
        netid = cas.authenticate()
        pageType = "undergraduates"
        role = uservalidation(netid)
        check = checkuser(role, pageType)

        # determine whether this is the user's first login
        if not check:
            return loginfail()
        else:
            useraccount = userAccount(netid, role)
            login_user(useraccount)

        isFirstLogin = firstLogin(netid)
        if isFirstLogin:
            createNewStudent(netid)
            if not TESTING:
                mail.send(welcomeEmail(netid))

    html = render_template('index.html',
                           netid=netid,
                           isAdmin=isAdmin(netid),
                           isFirstLogin=isFirstLogin,
                           )

    response = make_response(html)
    return response

@app.route('/search', methods=['GET'])
# @login_required
def searchResults():
    dept = request.args.get('dept')
    coursenum = request.args.get('coursenum')

    courses = search(dept, coursenum)

    html = '<table class=\"table table-striped\"> ' \
           '<thead> ' \
           '<tr> ' \
           '<th align = \"left\">Dept</th> ' \
           '<th align = \"left\">Num</th> ' + \
           '<th align = \"left\">Title</th> ' + \
           '<th align = \"right\">  </th> ' + \
           '<th align = \"right\">  </th> ' + \
           '</tr>' + \
           '</thead>' \
           '<tbody> '
    for course in courses:
        # numgroups = numberGroupsInClass(course.getDept(), course.getNum())

        html += '<tr>\n' + \
                '<td> ' + course.getDept() + ' </td>\n' + \
                '<td> ' + course.getNum() + ' </td>\n' + \
                '<td> ' + course.getTitle() + ' </td>\n'
        html += '<td> ' + '<span class="badge badge-primary badge-pill">group</span>' + ' </td>\n'
        html += '<td> ' + '<button type="button" class="btn btn-danger" id="joinGroup" ' \
                + 'dept="' + str(course.getDept()) + '" num="' + str(course.getNum()) \
                + '" onclick="joinClass(this)"> <h6>Join</h6> </button>' + ' </td>\n </tr>\n'

    html += '</tbody></table>'
    response = make_response(html)
    return response


@app.route('/joinClass', methods=['GET'])
# @login_required
def joinStudentToClass():
    netid = NETID
    if not LOCAL:
        netid = cas.authenticate()
        pageType = "undergraduates"
        role = uservalidation(netid)
        check = checkuser(role, pageType)
        if not check:
            return loginfail()

    dept = request.args.get('dept')
    num = request.args.get('num')

    # if isStudentInClass(netid, dept, coursenum):
    #     html = '<br><div class="alert alert-danger" role="alert">' + \
    #            'You\'ve already joined a group for this class!</div>'
    #     response = make_response(html)
    #     return response

    groupId = _addStudentToClass(netid, dept, num)

    # html = ''
    # html += '<br>'
    # html += '<div class="alert alert-success" role="alert">'
    # html += '<p>Successfully joined group! <br>'
    # html += 'View your group in the "My Groups" tab.</p>'
    # html += '</div>'

    response = make_response()
    return response

# -----------------------------------------------------------------------
# ADMIN BREAKDOWN AND GENERAL SITE ADMIN
# -----------------------------------------------------------------------
# About: include some info about the site
@app.route('/admin')
# @login_required
def admin():
    netid = NETID
    if not LOCAL:
        netid = cas.authenticate()
        pageType = "special"
        role = uservalidation(netid)
        check = checkuser(role, pageType)
        if not check:
            return loginfail(netid)

    html = render_template('admin.html',
                           netid=netid,
                           isAdmin=isAdmin(netid),
                           curr_admin=getAdmin(),
                           curr_faculty=getFaculty(),
                           breakdown=getAdminBreakdown(),
                           alert=['None', 'None', 'None', 'None'],
                           )
    response = make_response(html)
    return response

@app.route('/start_new_semester')
#login_required
def start_new_semester():
    netid = NETID
    if not LOCAL:
        netid = cas.authenticate()
        pageType = "special"
        role = uservalidation(netid)
        check = checkuser(role, pageType)
        if not check:
            return loginfail(netid)
    
    sem = request.args.get('sem')
    year = request.args.get('year')

    # calculate term number - starting point:
    # 1222 = Fall 2021, 
    term = 1222 + 3 * (int(year) - 2022)
    if sem =="fall":
        term += 3
    elif sem == "spring":
        term += 1
    elif sem == "summer":
        term += 2
    
    reset_classes(term)
    
    html = render_template('admin.html',
                           netid=netid,
                           isAdmin=isAdmin(netid),
                           curr_admin=getAdmin(),
                           curr_faculty=getFaculty(),
                           breakdown=getAdminBreakdown(),
                           alert=['None', 'None', 'None', 'None'],
                           )
    response = make_response(html)
    return response
    



# ------------------------------------------------------------------------------
# EDIT COURSE INFORMATION AND MANUAL GROUP INTERVENTION
# ------------------------------------------------------------------------------
@app.route('/admin_courses')
# @login_required
def admin_courses():
    print('in admin courses')
    netid = NETID
    if not LOCAL:
        netid = cas.authenticate()
        pageType = "special"
        role = uservalidation(netid)
        check = checkuser(role, pageType)
        if not check:
            return loginfail()
        useraccount = userAccount(netid, role)
        login_user(useraccount)

    html = render_template('admin_courses.html',
                           netid=netid,
                           isAdmin=isAdmin(netid),
                           )
    response = make_response(html)
    return response

@app.route('/searchAdmin', methods=['GET'])
# @login_required
def searchAdminResults():
    dept = request.args.get('dept')
    coursenum = request.args.get('coursenum')

    courses = search(dept, coursenum)

    html = '<table class=\"table table-striped\"> ' \
           '<thead> ' \
           '<tr> ' \
           '<th align = \"left\">Dept</th> ' \
           '<th align = \"left\">Num</th> ' + \
           '<th align = \"left\">Title</th> ' + \
           '<th align = \"right\">  </th> ' + \
           '</tr>' + \
           '</thead>' \
           '<tbody> '
    for course in courses:

        html_form = '<form action="edit_course" method="get">\
            <input type="hidden" name="dept" value=' + course.getDept() + '>\
            <input type="hidden" name="classnum" value=' + course.getNum() + '>\
            <input type="submit" class="btn" value="Edit Course Information">\
        </form>'

        html += '<tr>\n' + \
                '<td> ' + course.getDept() + ' </td>\n' + \
                '<td> ' + course.getNum() + ' </td>\n' + \
                '<td> ' + course.getTitle() + ' </td>\n'
        html += '<td> ' + html_form + '</td>\n'

    html += '</tbody></table>'
    response = make_response(html)
    return response

@app.route('/edit_course', methods=['GET'])
# @login_required
def edit_course():
    netid = NETID
    if not LOCAL:
        netid = cas.authenticate()
        pageType = "special"
        role = uservalidation(netid)
        check = checkuser(role, pageType)
        if not check:
            return loginfail(netid)

    dept = request.args.get('dept')
    classnum = request.args.get('classnum')


    course = getCourse(dept, classnum)
    group_overview = getGroupsInClass(dept, classnum)
    groups = []
    for g in group_overview:
        groups.append([g, getStudentsInGroup(g.getGroupId())])

    html = render_template('admin_edit_course.html',
                            netid=netid,
                            isAdmin=isAdmin(netid),
                            course=course,
                            groups=groups,
                            )
    response = make_response(html)
    return response


@app.route("/submit_course_edits")
# @login_required
def submit_course_edits():
    netid = NETID
    if not LOCAL:
        netid = cas.authenticate()
        pageType = "special"
        role = uservalidation(netid)
        check = checkuser(role, pageType)
        if not check:
            return loginfail(netid)

    dept = request.args.get('dept')
    classnum = request.args.get('classnum')
    status = request.args.get('status')
    if status == "Pending":
        endorse_status = 1
    elif status == "Denied":
        endorse_status = 0
    else:
        endorse_status = 2
    notes = request.args.get('notes')

    action = approveCourse(dept, classnum, endorse_status, notes)
    if action is not None:
        if action[0] == 0:
            if not TESTING:
                mail.send(courseDeniedEmail(action[1], dept, classnum))
        if action[0] == 2:
            if not TESTING:
                mail.send(courseApprovedEmail(action[1], dept, classnum))

    html = render_template('admin_courses.html',
                           netid=netid,
                           isAdmin=isAdmin(netid),
                           )
    response = make_response(html)
    return response


# ------------------------------------------------------------------------------
# ABOUT
# ------------------------------------------------------------------------------
@app.route('/about')
# @login_required
def about():
    netid = NETID
    if not LOCAL:
        netid = cas.authenticate()
        pageType = "undergraduates"
        role = uservalidation(netid)
        check = checkuser(role, pageType)
        if not check:
            return loginfail()

    html = render_template('about.html',
                           netid=netid,
                           isAdmin=isAdmin(netid),
                           )
    response = make_response(html)
    return response



# ------------------------------------------------------------------------------
# LOGOUT
# ------------------------------------------------------------------------------
@app.route('/logout')
def logout():
    netid = NETID
    if not LOCAL:
        netid = cas.authenticate()
        cas.logout()


# ------------------------------------------------------------------------------
# TESTING
# ------------------------------------------------------------------------------
@app.route('/testing')
def testing():
    html = render_template('loginfail.html',
    )
    response = make_response(html)
    return response




# -----------------------------------------------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(argv[1]), debug=True)
