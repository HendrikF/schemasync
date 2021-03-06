#!python
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
consolehandler = logging.StreamHandler()
consolehandler.setLevel(logging.DEBUG)
consoleformatter = logging.Formatter('%(name)s\t%(levelname)s\t%(message)s')
consolehandler.setFormatter(consoleformatter)
logger.addHandler(consolehandler)

from schemasync.Schemasync import Schemasync
from schemasync.dialects.PostgreSQL import PostgreSQL

import psycopg2 as dbapi

connection = dbapi.connect(host='localhost', database='test', user='test', password='test')

dialect = PostgreSQL(dbapi, connection)

schemasync = Schemasync(dialect)

changesets = []
changeset = changesets.append

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

@changeset
def refactorTablePersonToEmployee():
    yield RenameTable('person', 'employee')
    yield AddColumns('employee', [
        Column('street', 'varchar', 200),
        Column('streetNo', 'varchar', 20),
        Column('zipcode', 'varchar', 20),
        Column('city', 'varchar', 200),
    ])

@changeset
def testOtherChanges():
    yield CreateTable('temp', [
        Column('id', 'auto', primaryKey=True),
        Column('firstname', 'varchar', 200, null=False),
        Column('lastname', 'varchar', 200, null=False),
    ])
    yield AddColumns('temp', [
        Column('test', 'varchar', 200),
        Column('birthday', 'datetime'),
    ])
    yield DropColumns('temp', ['firstname', 'lastname'])
    yield DropTable('temp')

@changeset
def renameColumn():
    yield RenameColumn('employee', 'streetNo', 'streetno')

@changeset
def createHibernateSequence():
    yield CreateSequence('hibernate_seuqence', minValue=100, incrementBy=3)

# If you have errors like this typo in your changesets,
# then do not modify the changeset, but add another changeset.
# This is because the corrected changeset will not be executed again.
@changeset
def fixTypoInHibernateSequence():
    yield RenameSequence('hibernate_seuqence', 'hibernate_sequence')

schemasync.process(changesets)
