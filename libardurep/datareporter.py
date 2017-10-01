"""
MODULE:       datareporter
PURPOSE:      get the date from the store and report it.
AUTHOR(S):    michael lustenberger inofix.ch
COPYRIGHT:    (C) 2017 by Michael Lustenberger and INOFIX GmbH

              This program is free software under the GNU General Public
              License (v3).
"""

from base64 import b64encode
import httplib
import re
import requests
import urllib2

class DataReporter(object):
    """
    This class has a data store associated and reports the data
    to a given URL on request.
    """

    def __init__(self, store, url="", credentials={}, do_verify_certificate=True):
        """
        Initialize the reporter.
            store store         the data store
        """
        self.store = store
        # for commodity, either register url etc. or choose every time
        self.url = url
        self.credentials = credentials
        self.do_verify_certificate = do_verify_certificate

    def log(self, url=None, credentials=None, do_verify_certificate=True):
        """
        Wrapper for the other log methods, decide which one based on the
        URL parameter.
        """
        if url is None:
            url = self.url
        if re.match("file://", url):
            self.log_file(url)
        elif re.match("https://", url) or re.match("http://", url):
            self.log_post(url, credentials, do_verify_certificate)
        else:
            self.log_stdout()

    def log_stdout(self):
        """
        Write to standard output
        """
        print self.store.get_text()

    def log_file(self, url=None):
        """
        Write to a local log file
        """
        if url is None:
            url = self.url
        f = re.sub("file://", "", url)
        try:
            with open(f, "a") as of:
                of.write(str(self.store.get_json_tuples(True)))
        except IOError as e:
            print e
            print "Could not write the content to the file.."

    def log_post(self, url=None, credentials=None, do_verify_certificate=True):
        """
        Write to a remote host via HTTP POST
        """
        if url is None:
            url = self.url
        if credentials is None:
            credentials = self.credentials
        if do_verify_certificate is None:
            do_verify_certificate = self.do_verify_certificate
        if credentials and credentials.has_key("base64"):
            headers = {"Content-Type": "application/json", \
                        'Authorization': 'Basic %s' % credentials["base64"]}
        else:
            headers = {"Content-Type": "application/json"}
        try:
            request = requests.post(url, headers=headers, \
                    data=self.store.get_json(), verify=do_verify_certificate)
        except httplib.IncompleteRead as e:
            request = e.partial

    def log_ssh(self):
        """
        Write to a remote file via ssh
        """
        pass

    def register_credentials(self, credentials=None, user=None, user_file=None, password=None, password_file=None):
        """
        Helper method to store username and password
        """
        # lets store all kind of credential data into this dict
        if credentials is not None:
            self.credentials = credentials
        else:
            self.credentials = {}
            # set the user from CLI or file
            if user:
                self.credentials["user"] = user
            elif user_file:
                with open(user_file, "r") as of:
                    # what would the file entry look like?
                    pattern = re.compile("^user: ")
                    for l in of:
                        if re.match(pattern, l):
                            # strip away the newline
                            l = l[0:-1]
                            self.credentials["user"] = re.sub(pattern, "", l)
                # remove any surrounding quotes
                if self.credentials["user"][0:1] == '"' and \
                                    self.credentials["user"][-1:] == '"':
                    self.credentials["user"] = self.credentials["user"][1:-1]
            # set the password from CLI or file
            if password:
                self.credentials["password"] = password
            elif password_file:
                with open(password_file, "r") as of:
                    # what would the file entry look like?
                    pattern = re.compile("^password: ")
                    for l in of:
                        if re.match(pattern, l):
                            # strip away the newline
                            l = l[0:-1]
                            self.credentials["password"] = \
                                                    re.sub(pattern, "", l)
                # remove any surrounding quotes
                if self.credentials["password"][0:1] == '"' and \
                                    self.credentials["password"][-1:] == '"':
                    self.credentials["password"] = \
                                        self.credentials["password"][1:-1]

            # if both user and password is set,
            #  1. encode to base 64 for basic auth
            if self.credentials.has_key("user") and \
                            self.credentials.has_key("password"):
                self.credentials["base64"] = b64encode(self.credentials["user"]\
                        + ":" + self.credentials["password"]).decode("ascii")

