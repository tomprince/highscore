#! /usr/bin/env python

import getpass
import readline
assert readline # here for side-effects

from twisted.internet import reactor
from twisted.python import log

from txgithub import token

def printToken(token):
    print("Add\n\toauth2_token=%r\nto your highscore.tac in the github "
            "plugin section." % (token,))

def main(username, password):
    d = token.getToken(username, password,
            note="Highscore", note_url='https://github.com/djmitche/highscore',
            scopes = [ 'public_repo' ]
            )
    d.addCallback(printToken)
    d.addErrback(log.err)
    d.addBoth(lambda _: reactor.stop())
    return d

username = raw_input("github username: ")
password = getpass.getpass("github password: ")
reactor.callWhenRunning(main, username, password)
reactor.run()
