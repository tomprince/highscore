from txgithub import api
from twisted.python import log, usage
from twisted.application import service
from twisted import plugin
from zope.interface import implements

class Options(usage.Options):
    synopsis = "[-t <token>] <files>"
    optParameters = [["token", "t", None, "oauth token"]]

    compData = usage.Completions(
        optActions={"log": usage.CompleteFiles("*.log"),
                    "interface": usage.CompleteNetInterfaces()}
        )

    longdesc = "Posts a gist."

    def parseArgs(self, *files):
        self['files'] = files

    def postOptions(self):
        if not self['token']:
            raise usage.UsageError("Specifying a token is required.")

class Service(service.Service):
    def __init__(self, token, files):
        self.api = api.GithubApi(token)
        self.files = files

    def startService(self):
        from twisted.internet import reactor
        files = {}
        if self.files:
            for name in self.files:
                with open(name) as f:
                    files[name] = {"content": f.read()}
        else:
            import sys
            files['gistfile1'] = {"content": sys.stdin.read()}
        d = self.api.gists.create(files=files)
        @d.addCallback
        def printUrl(res):
            print res['html_url']
        d.addErrback(log.err)
        d.addBoth(lambda _: reactor.stop())

class MyServiceMaker(object):
    implements(service.IServiceMaker, plugin.IPlugin)
    tapname = "gist"
    description = "gist poster"
    options = Options

    def makeService(self, config):
        return Service(files=config['files'], token=config['token'])

serviceMaker = MyServiceMaker()
