import os

from pymongo import MongoClient
from pymongo import errors

class MongoDB(object):

    def initialize(self):
        try:
            client = MongoClient(os.getenv("MONGO_URI"))
            db = client[os.getenv("MONGO_DATABASE")]
            return db
        except errors.ConnectionFailure as e:
            print('Could not connect to MongoDB:', e)

    def close(self, db):
        db.client.close()