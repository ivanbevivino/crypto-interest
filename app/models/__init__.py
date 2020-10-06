import sqlalchemy

from ..extensions import db


from .interest import Interest


sqlalchemy.orm.configure_mappers()
