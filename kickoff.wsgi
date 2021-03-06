from ConfigParser import RawConfigParser
import logging
from os import getenv
from os import path
import site

try:
    import newrelic.agent
except ImportError:
    newrelic = False
if newrelic:
    newrelic_ini = getenv('NEWRELIC_PYTHON_INI_FILE')
    if newrelic_ini:
        newrelic.agent.initialize(newrelic_ini)

mydir = path.dirname(path.abspath(__file__))
site.addsitedir(mydir)
site.addsitedir(path.join(mydir, 'vendor/lib/python'))

from kickoff import db, app as application
from kickoff.log import cef_config

cfg = RawConfigParser()
cfg.read(path.join(mydir, 'kickoff.ini'))
dburi = cfg.get('database', 'dburi')
logfile = cfg.get('logging', 'logfile')
loglevel = logging.getLevelName(cfg.get('logging', 'level'))
cef_logfile = cfg.get('logging', 'cef_logfile')
secretKey = cfg.get('app', 'secret_key')

logging.basicConfig(filename=logfile, level=loglevel, format='%(asctime)s - %(name)s.%(funcName)s#%(lineno)s: %(message)s')
application.config['SQLALCHEMY_DATABASE_URI'] = dburi
application.config['SQLALCHEMY_POOL_RECYCLE'] = 60
application.config['SECRET_KEY'] = secretKey
application.config.update(cef_config(cef_logfile))
with application.test_request_context():
    db.init_app(application)

if newrelic:
    application = newrelic.agent.wsgi_application()(application)
