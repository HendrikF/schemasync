from sqlalchemy.exc import ProgrammingError, InternalError
import time

from .. import *

class postgresql:
    systemTableLock = 'schemasync_lock'
    systemTableChangelog = 'schemasync_changelog'
    
    currentDatetime = lambda self: time.strftime('%Y-%m-%d %H:%M:%S')
    
    def __init__(self, connection):
        self.connection = connection
    
    def run(self, changesets):
        self.ensureLockExists()
        self.lock()
        try:
            self.ensureChangelogExists()
            self.changsetsDone = self.readChangelogTable()
            changesets = self.filterChangesets(changesets)
            self.processChangesets(changesets)
        finally:
            self.release()
    
    def ensureLockExists(self):
        try:
            for row in self.connection.execute('SELECT id FROM {} WHERE id=1'.format(self.systemTableLock)):
                pass
        except ProgrammingError as e:
            self.connection.execute('''CREATE TABLE {0}
(
  id integer NOT NULL,
  CONSTRAINT {0}_pkey PRIMARY KEY (id)
);'''.format(self.systemTableLock))
    
    def lock(self):
        """ We insert the same value every time as primary key, which only works once
        """
        try:
            self.connection.execute('INSERT INTO {} (id) VALUES (1)'.format(self.systemTableLock))
        except:
            raise RuntimeError('Unable to aquire lock')
    
    def release(self):
        self.connection.execute('DELETE FROM {} WHERE id=1'.format(self.systemTableLock))
        self.connection.close()
    
    def ensureChangelogExists(self):
        try:
            for row in self.connection.execute('SELECT id FROM {} LIMIT 1'.format(self.systemTableChangelog)):
                pass
        except ProgrammingError as e:
            self.connection.execute('''CREATE TABLE {0}
(
  id serial NOT NULL,
  name character varying(200) NOT NULL,
  datetime character varying(30) NOT NULL,
  CONSTRAINT {0}_pkey1 PRIMARY KEY (id),
  CONSTRAINT {0}_name_key UNIQUE (name)
);'''.format(self.systemTableChangelog))
    
    def readChangelogTable(self):
        return [name for name, in self.connection.execute('SELECT name FROM {}'.format(self.systemTableChangelog))]
    
    def filterChangesets(self, changesets):
        newChangesets = []
        for changeset in changesets:
            if changeset.__name__ not in self.changsetsDone:
                newChangesets.append(changeset)
        return newChangesets
    
    def processChangesets(self, changesets):
        for changeset in changesets:
            with self.connection.begin() as transaction:
                for change in changeset():
                    if isinstance(change, createTable):
                        sql = 'CREATE TABLE "{}"\n(\n'.format(change.name)
                        constraints = ''
                        colnum = 0
                        for column in change.columns:
                            colnum += 1
                            sql += '  "{}" {}'.format(column.name, self.mapColumnTypes(column.type))
                            if column.length:
                                sql += '({})'.format(column.length)
                            if not column.null:
                                sql += ' NOT NULL,\n'
                            if column.primaryKey:
                                constraints += '  CONSTRAINT "{}_pkey{}" PRIMARY KEY ("{}"),\n'.format(change.name, colnum, column.name)
                            if column.unique:
                                constraints += '  CONSTRAINT "{0}_{1}_key" UNIQUE ("{1}"),\n'.format(change.name, column.name)
                        sql += constraints
                        sql = sql.strip(',\n')
                        sql += '\n);'
                        self.connection.execute(sql);
                # changelog
                self.connection.execute('''INSERT INTO {} (name, datetime) VALUES ('{}', '{}');'''.format(
                    self.systemTableChangelog, changeset.__name__, self.currentDatetime()))
    
    def mapColumnTypes(self, name):
        if name == 'varchar':
            return 'character varying'
        return name
