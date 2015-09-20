#!python
from schemasync.Schemasync import Schemasync
from schemasync.dialects.PostgreSQL import PostgreSQL

import psycopg2 as dbapi

connection = dbapi.connect(host='localhost', database='test', user='test', password='test')

dialect = PostgreSQL(dbapi, connection)

schemasync = Schemasync(dialect)

changesets = []
def changeset(func):
    changesets.append(func)
    return func

from schemasync.changes import *
from schemasync.definitions import *

@changeset
def createTablePerson():
    yield CreateTable('person', [
        Column('id', 'auto', primaryKey=True),
        Column('firstname', 'varchar', 200, null=False),
        Column('lastname', 'varchar', 200, null=False),
    ], constraints=[
        UniqueConstraint('name', ('firstname', 'lastname')),
    ])

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
consolehandler = logging.StreamHandler()
consolehandler.setLevel(logging.DEBUG)
consoleformatter = logging.Formatter('%(name)s\t%(levelname)s\t%(message)s')
consolehandler.setFormatter(consoleformatter)
logger.addHandler(consolehandler)

schemasync.process(changesets)
