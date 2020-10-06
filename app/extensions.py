from flask_sqlalchemy import SQLAlchemy
# from app.helpers.continuum import ManualUnitOfWork, ManualVersioningManager, make_versioned
from sqlalchemy_continuum import make_versioned
from sqlalchemy_continuum.plugins import ActivityPlugin

db = SQLAlchemy()

activity_plugin = ActivityPlugin()
make_versioned(user_cls=None, plugins=[activity_plugin])
