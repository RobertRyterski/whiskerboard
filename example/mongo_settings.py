AUTHENTICATION_BACKENDS = (
    'mongoengine.django.auth.MongoEngineBackend',
)

SESSION_ENGINE = 'mongoengine.django.sessions'

db_name = "whiskerboard"

from mongoengine.connection import connect
MONGO_CONNECTION = connect(db_name, host='localhost')

MONGO_DATABASE_NAME = db_name
