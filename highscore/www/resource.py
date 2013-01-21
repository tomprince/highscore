# This file is part of Buildbot.  Buildbot is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright Buildbot Team Members

import json
from twisted.python import log
from twisted.internet import defer
from twisted.web import resource, server

class Resource(resource.Resource):

    contentType = 'text/html'

    def __init__(self, highscore):
        resource.Resource.__init__(self)
        self.highscore = highscore

    def render(self, request):
        d = defer.maybeDeferred(lambda : self.content(request))
        def handle(data):
            if isinstance(data, unicode):
                data = data.encode("utf-8")
            request.setHeader("content-type", self.contentType)
            if request.method == "HEAD":
                request.setHeader("content-length", len(data))
                return ''
            return data
        d.addCallback(handle)
        def ok(data):
            request.write(data)
            try:
                request.finish()
            except RuntimeError:
                # this occurs when the client has already disconnected; ignore
                # it (see #2027)
                log.msg("http client disconnected before results were sent")
        def fail(f):
            request.processingFailed(f)
            return None # processingFailed will log this for us
        d.addCallbacks(ok, fail)
        return server.NOT_DONE_YET

    def content(self, request):
        return ''

class UsersPointsResource(Resource):
    contentType = 'application/json'

    def getChild(self, name, request):
        try:
            userid = int(name)
        except:
            return Resource.getChild(self, name, request)
        return UserPointsResource(self.highscore, userid)

    @defer.inlineCallbacks
    def content(self, request):
        scores = yield self.highscore.points.getHighscores()
        defer.returnValue(json.dumps(scores))


class UserPointsResource(Resource):
    contentType = 'application/json'

    def __init__(self, highscore, userid):
        Resource.__init__(self, highscore)
        self.userid = userid

    @defer.inlineCallbacks
    def content(self, request):
        points = yield self.highscore.points.getUserPoints(self.userid)
        name = yield self.highscore.users.getDisplayName(self.userid)
        defer.returnValue(json.dumps({'name':name, 'points':points}))


class ApiResource(Resource):
    contentType = 'application/json'

    def __init__(self, highscore):
        Resource.__init__(self, highscore)
        self.putChild('user', UsersPointsResource(highscore))


class PluginsResource(Resource):

    def __init__(self, highscore):
        Resource.__init__(self, highscore)
        self.highscore = highscore

    def getChild(self, name, request):
        if name in self.highscore.plugins:
            plugin = self.highscore.plugins[name]
            if plugin.www:
                return plugin.www
        return Resource.getChild(self, name, request)
