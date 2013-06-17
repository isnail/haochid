__author__ = 'biyanbing'
import sae
import wsgi

application = sae.create_wsgi_app(wsgi.application)