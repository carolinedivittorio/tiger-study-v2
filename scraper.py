"""
Adapted from TigerPath's Scraper (@ tigerpath.io)

Scrapes OIT's Web Feeds to add courses and sections to database.
Procedure:
- Get list of departments (3-letter department codes)
- Run this: http://etcweb.princeton.edu/webfeeds/courseofferings/?term=current&subject=COS
- Parse it for courses
"""

from lxml import etree
from html.parser import HTMLParser
from urllib.request import urlopen
import re
import ssl
import pprint

ssl.SSLContext.verify_mode = ssl.VerifyMode.CERT_OPTIONAL
ssl._create_default_https_context = ssl._create_unverified_context

# TERM_CODE = 'current'
TERM_CODE='1222' #Fall21
COURSE_OFFERINGS = "http://registrar.princeton.edu/course-offerings/"
FEED_PREFIX = "http://etcweb.princeton.edu/webfeeds/courseofferings/"
TERM_PREFIX = FEED_PREFIX + "?term=" + str(TERM_CODE)
DEP_PREFIX = TERM_PREFIX + "&subject="
VERSION_PREFIX = "&vers=1.5"

CURRENT_SEMESTER = ['']

h = HTMLParser()
pp = pprint.PrettyPrinter(indent=4)


class ParseError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def get_text(key, object, fail_ok=False):
    found = object.find(key)
    if fail_ok and (found is None or found.text is None):
        return found
    elif (found is None or found.text is None):
        ParseError("key " + key + " does not exist")
    else:
        return found.text


def remove_namespace(doc, namespace):
    """Hack to remove namespace in the document in place.
    """
    ns = u'{%s}' % namespace
    nsl = len(ns)
    for elem in doc.getiterator():
        if elem.tag.startswith(ns):
            elem.tag = elem.tag[nsl:]


def scrape(department, term):
    """ Scrape all events listed under department
    """
    PTON_NAMESPACE = u'http://as.oit.princeton.edu/xml/courseofferings-1_5'
    parser = etree.XMLParser(ns_clean=True)
    link = DEP_PREFIX + department + VERSION_PREFIX
    xmldoc = urlopen(link)
    tree = etree.parse(xmldoc, parser)
    dep_courses = tree.getroot()
    remove_namespace(dep_courses, PTON_NAMESPACE)
    parsed_courses = []
    for term in dep_courses:
        for subjects in term:
            for subject in subjects:
                dept = get_text('code', subject, fail_ok=True)
                for courses in subject:
                    for course in courses:
                        x = parse_course(course, subject)
                        if x is not None and dept == department:
                            x["dept"] = dept
                            parsed_courses.append(x)
    return parsed_courses

def parse_course(course, subject):
    """ create a course with basic information.
    """
    try:
        return {
            "title": get_text('title', course),
            "coursenum": get_text('catalog_number', course),
        }
    except Exception as inst:
        raise inst


if __name__ == '__main__':
    res = scrape("COS", TERM_CODE)
    pp.pprint(res)