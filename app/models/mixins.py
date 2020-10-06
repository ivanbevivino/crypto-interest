from . import db
from datetime import datetime
from app.extensions import activity_plugin
from flask import current_app
from sqlalchemy.types import Boolean
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy_continuum import version_class
import json
import sqlalchemy
import re
from enum import Enum
from sqlalchemy.orm import mapper
from sqlalchemy import event



class BaseModel(db.Model):
    __abstract__ = True

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # status = db.Column(db.String(20), default='active')

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def comparable_fields(self):
        return ["display_id"]

    def relationship_fields(self):
        return {}

    def save(self, verb=u'create'):
        try:
            # db.session.add(self)
            # db.session.commit()

            db.session.add(self)
            db.session.flush()
            _activity_class = activity_plugin.activity_cls
            activity = _activity_class(verb=verb, object=self)
            db.session.add(activity)
            db.session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            db.session.rollback()
            if "UNIQUE constraint failed:" in e.args[0]:
                match = re.match(".*UNIQUE constraint failed: ([a-zA-Z\.]+)", e.args[0])
                raise Exception(
                    "{} already exists.".format(match[1]).replace(".", " ")
                )
            elif re.match(".*Duplicate entry .* for key 'ix_([a-zA-Z\_]+)'", e.args[0]):
                match = re.match(
                    ".*Duplicate entry .* for key 'ix_([a-zA-Z\_]+)'", e.args[0]
                )
                raise Exception(
                    "{} already exists.".format(match[1]).replace("_", " ")
                )
            elif re.match(".*Duplicate entry (.*) for key '([a-zA-Z\_]+)'", e.args[0]):
                match = re.match(
                    ".*Duplicate entry (.*) for key '([a-zA-Z\_]+)'", e.args[0]
                )
                raise Exception(
                    "{} already exists.".format(match[1]).replace("-", " ")
                )
            elif re.match(".*Column (.*) cannot be null.*", e.args[0]):
                match = re.match(
                    ".*Column (.*) cannot be null.*", e.args[0]
                )
                raise Exception(
                    "Column {} cannot be null.".format(match[0])
                )

            else:
                raise e
        except:
            db.session.rollback()
            raise

    def generate_display_id(self):
        return ""

    def delete(self, force_children_unlink=False):
        try:
            db.session.delete(self)
            db.session.flush()

            _activity_class = activity_plugin.activity_cls
            activity = _activity_class(verb=u'delete', object=self)
            db.session.add(activity)

            db.session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            db.session.rollback()
            if "Cannot delete or update a parent row" in e.args[0]:
                raise Exception(
                    "Cannot delete {} with children.".format(self.__class__.__name__)
                )
            else:
                raise e
        except Exception:
            db.session.rollback()
            raise

    def populate(self, d, allowed_keys):
        {setattr(self, k, v) for k, v in d.items() if k in allowed_keys}
        return self

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.save(verb=u'update')
        return self

    @classmethod
    def list_by(cls, filters, transaction_id=None):
        current_app.logger.info("Querying {} with params {}".format(cls.__name__, json.dumps(filters)))

        # if(filters.get('tmp') is not None):
        #     # converting these values to boolean True or False
        #     filters['tmp'] = filters.get('tmp') in ['true', '1', 1, 'True', True]

        if transaction_id is not None:
            return cls._transaction_query(filters, transaction_id)

        return cls.query.filter_by(**filters)

    @classmethod
    def list_allowed_filters(cls):
        return []

    @classmethod
    def create(cls, **kwargs):
        cls.validate_create_payload(**kwargs)
        instance = cls(**kwargs)
        instance.save()
        return instance

    @classmethod
    def validate_create_payload(cls, **kwargs):
        required_fields = cls.creation_required_fields()
        for k in required_fields:
            if k not in kwargs.keys():
                raise Exception("{} is required to create {}".format(k, cls.__name__), 400)

    @classmethod
    def find(cls, id, transaction_id=None):
        if transaction_id is not None:
            try:
                return cls._transaction_query({'id': id}, transaction_id).one()
            except (MultipleResultsFound, NoResultFound):
                raise Exception("{} with ID {} not found.".format(cls, id), 404)

        i = cls.query.get(id)
        if i is None:
            raise Exception("{} with ID {} not found.".format(cls, id), 404)
        return i

    @classmethod
    def find_by_display_id(cls, id, transaction_id=None):
        i = cls.list_by({'display_id': id}, transaction_id=transaction_id).first()
        if i is None:
            raise Exception("{} with key: {} and value: {} not found.".format(cls, 'display_id', id), 404)
        return i

    @classmethod
    def find_by(cls, key, value, transaction_id=None):
        i = cls.list_by({key: value}, transaction_id=transaction_id).first()
        if i is None:
            raise Exception("{} with {}: {} not found.".format(cls, key, value), 404)
        return i

    @classmethod
    def delete_all(cls):
        try:
            # TODO: update delete_all

            query = cls.__table__.delete()
            db.session.execute(query)
            db.session.commit()
        except:
            db.session.rollback()
            raise

    @classmethod
    def creation_required_fields(cls):
        return []

    @classmethod
    def _transaction_query(cls, filters, transaction_id):
        version_cls = version_class(cls)
        return db.session.query(version_cls).filter_by(**filters, transaction_id=transaction_id)

    @classmethod
    def get_for_compare(cls, filters, transaction_id):
        results = cls.list_by(filters, transaction_id=transaction_id)
        return {getattr(r, 'id', ''): {k: v for k, v in r.__dict__.items() if k not in (
        '_sa_instance_state', 'created_at', 'updated_at', 'transaction_id', 'end_transaction_id', 'operation_type')} for
                r in results}

    @classmethod
    def bulk_update(cls, objects):
        try:
            # TODO: update bulk_save_objects
            db.session.bulk_save_objects(objects)
            db.session.commit()
        except:
            db.session.rollback()
            raise

    def equals(self, other):
        if type(other) is self.__class__:
            try:
                return all(map(lambda field: getattr(self, field) == getattr(other, field), self.comparable_fields()))
            except AttributeError:
                return False

        return False

