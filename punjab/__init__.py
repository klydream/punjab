"""
Punjab - multiple http interfaces to jabber.

"""
from twisted.python import log
from twisted.application import service


def uriCheck(elem, uri):
    """
    This is a hack for older versions of twisted words, we need to get rid of it.
    """
    if str(elem.toXml()).find('xmlns') == -1:
        elem['xmlns'] = uri

class Service(service.Service):
    """
    Punjab generice service
    """
    def error(self, failure, body = None):
        """
        A Punjab error has occurred
        """
        # need a better way to trap this
        if failure.getErrorMessage() != 'remote-stream-error':
            log.msg('Punjab Error: ')
            log.msg(failure.printBriefTraceback())
            log.msg(body)
        failure.raiseException()                
        
            
    def success(self, result, body = None):
        """
        If success we log it and return result
        """
        log.msg(body)
        return result



def makeService(config):
    """
    Create a punjab service to run
    """
    from twisted.web import  server, resource, static
    from twisted.application import service, internet

    import httpb


    serviceCollection = service.MultiService()

    if config['html_dir']:
        r = static.File(config['html_dir'])
    else:
        print "The html directory is needed."
        return

    

    if config['httpb']:
        b = httpb.HttpbService(config['verbose'], config['polling'])
        r.putChild('httpb', resource.IResource(b))


    site  = server.Site(r)


    if config['ssl']:
        from twisted.internet import ssl
        from OpenSSL import SSL
        ssl_context = ssl.DefaultOpenSSLContextFactory(config['ssl_privkey'],
                                                       config['ssl_cert'],
                                                       SSL.SSLv23_METHOD,)
        sm = internet.SSLServer(int(config['port']),
                                site,
                                ssl_context,
                                backlog = int(config['verbose']))
        sm.setServiceParent(serviceCollection)
    else:
        sm = internet.TCPServer(int(config['port']), site)
        
        sm.setServiceParent(serviceCollection)

    return sm

