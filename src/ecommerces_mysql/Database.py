import os
import mysql.connector

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

class MySQLDB(object):

    def __init__(self):
        self.conn = mysql.connector.connect(
            host = os.getenv("MYSQL_HOST"),
            user = os.getenv("MYSQL_USER"),
            password = os.getenv("MYSQL_PASSWORD"),
            database = os.getenv("MYSQL_DATABASE")
        )

        ## Create cursor, used to execute commands
        self.cur = self.conn.cursor()

        ## Create quotes table if none exists
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS products(
            product_id VARCHAR(255) NOT NULL,
            name VARCHAR(255),
            short_description VARCHAR(255),
            description LONGTEXT,
            url VARCHAR(255),
            rating FLOAT,
            selling_count BIGINT,
            price BIGINT,
            category_id INT,
            PRIMARY KEY (product_id)
        )
        """)

    def commit(self, query, params):
        self.cur.execute(query, params)
        self.conn.commit()

    def commitMany(self, query, params):
        self.cur.executemany(query, params)
        self.conn.commit()

    def fetchone(self, query, params):
        self.cur.execute(query, params)
        return self.cur.fetchone()

    def close(self):
        self.cur.close()
        self.conn.close()