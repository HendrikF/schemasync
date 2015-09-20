import time
import logging

from .Dialect import Dialect
from ..errors import LockError, UnknownChangeError

from ..changes import *
from ..definitions import *

class PostgreSQL(Dialect):
    class Transaction:
        log = logging.getLogger('schemasync.sql.transaction')
        
        def __init__(self, connection):
            self.connection = connection
        
        def __enter__(self):
            self.log.info('BEGIN')
            self.cursor = self.connection.cursor()
            return self.cursor
        
        def __exit__(self, exc_type, exc_value, traceback):
            self.cursor.close()
            if exc_type == exc_value == traceback == None:
                self.log.info('COMMIT')
                self.connection.commit()
            else:
                self.log.info('ROLLBACK')
                self.connection.rollback()
    
    columnTypes = {
        'auto': 'serial',
        'varchar': 'character varying',
        'datetime': 'timestamp without time zone',
    }
    
    log = logging.getLogger('schemasync.dialect.postgresql')
    logSQL = logging.getLogger('schemasync.sql')
    
    @classmethod
    def mapColumnType(cls, typ):
        return cls.columnTypes.get(typ, typ)
    
    @staticmethod
    def datetime():
        return time.strftime('%Y-%m-%d %H:%M:%S')
    
    def __init__(self, dbapi, connection):
        self.dbapi = dbapi
        self.c = connection
    
    def transaction(self):
        return self.Transaction(self.c)
    
    def lock(self):
        try:
            with self.transaction() as cur:
                cur.execute('SELECT id FROM "{0}" WHERE id=1;'.format(self.tableLock))
        except self.dbapi.ProgrammingError:
            self.log.info('Creating Changelog Lock')
            with self.transaction() as cur:
                cur.execute('''CREATE TABLE "{0}"
(
  id integer NOT NULL,
  CONSTRAINT "{0}_pkey" PRIMARY KEY (id)
);'''.format(self.tableLock))
        
        self.log.info('Acquiring Changelog Lock')
        try:
            with self.transaction() as cur:
                cur.execute('INSERT INTO "{0}" (id) VALUES (1);'.format(self.tableLock))
            self.log.info('Successfully acquired Changelog Lock')
        except self.dbapi.IntegrityError:
            raise LockError('Unable to acquire lock')
    
    def release(self):
        self.log.info('Releasing Changelog Lock')
        with self.transaction() as cur:
            cur.execute('DELETE FROM "{0}" WHERE id=1;'.format(self.tableLock))
        self.log.info('Successfully released Changelog Lock')
    
    def changeSetsDone(self):
        try:
            with self.transaction() as cur:
                cur.execute('SELECT id FROM "{0}" LIMIT 1;'.format(self.tableChangelog))
        except self.dbapi.ProgrammingError as e:
            self.log.info('Creating Changelog')
            with self.transaction() as cur:
                cur.execute('''CREATE TABLE "{0}"
(
  id serial NOT NULL,
  name character varying(200) NOT NULL,
  datetime timestamp without time zone NOT NULL,
  CONSTRAINT "{0}_pkey" PRIMARY KEY (id),
  CONSTRAINT "{0}_name_key" UNIQUE (name)
);'''.format(self.tableChangelog))
        
        self.log.info('Reading Changelog from Database')
        with self.transaction() as cur:
            cur.execute('SELECT name FROM "{0}" ORDER BY id;'.format(self.tableChangelog))
            changeSetsDone = cur.fetchall()
        self.log.info('Read %s entries from Changelog', len(changeSetsDone))
        return [changeSet[0] for changeSet in changeSetsDone]
    
    def process(self, changeSet):
        self.log.info('Processing Changeset %s', changeSet.__name__)
        with self.transaction() as cur:
            for change in changeSet():
                
                sql = ''
                
                if isinstance(change, CreateTable):
                    self.log.info('Creating Table')
                    sql = 'CREATE TABLE "{0}"\n(\n'.format(change.tableName)
                    constraints = ''
                    # columns
                    for column in change.columns:
                        sql += '  "{0}" {1}'.format(column.name, self.mapColumnType(column.type))
                        if column.length:
                            sql += '({0})'.format(column.length)
                        if not column.null:
                            sql += ' NOT NULL'
                        if column.primaryKey:
                            constraints += '  CONSTRAINT "{0}_{1}_pkey" PRIMARY KEY ("{1}"),\n'.format(change.tableName, column.name)
                        if column.unique:
                            constraints += '  CONSTRAINT "{0}_{1}_key" UNIQUE ("{1}"),\n'.format(change.tableName, column.name)
                        sql += ',\n'
                    # constraints
                    for constraint in change.constraints:
                        if isinstance(constraint, PrimaryKey):
                            constraints += '  CONSTRAINT "{0}_{1}_pkey" PRIMARY KEY ("{2}"),\n'.format(change.tableName, constraint.name, '", "'.join(constraint.columnNames))
                        elif isinstance(constraint, UniqueConstraint):
                            constraints += '  CONSTRAINT "{0}_{1}_key" UNIQUE ("{2}"),\n'.format(change.tableName, constraint.name, '", "'.join(constraint.columnNames))
                    # execute
                    sql += constraints
                    sql = sql.strip(',\n')
                    sql += '\n);'
                
                elif isinstance(change, RenameTable):
                    self.log.info('Renaming Table')
                    sql = 'ALTER TABLE "{0}" RENAME TO "{1}";'.format(change.oldName, change.newName)
                
                elif isinstance(change, DropTable):
                    self.log.info('Dropping Table')
                    sql = 'DROP TABLE "{0}";'.format(change.tableName)
                
                elif isinstance(change, AddColumns):
                    self.log.info('Adding Columns')
                    constraints = ''
                    for column in change.columns:
                        sql += 'ALTER TABLE "{0}" ADD COLUMN "{1}" {2}'.format(change.tableName, column.name, self.mapColumnType(column.type))
                        if column.length:
                            sql += ' ({0})'.format(column.length)
                        if not column.null:
                            sql += ' NOT NULL'
                        if column.primaryKey:
                            constraints += 'ALTER TABLE "{0}" ADD CONSTRAINT "{1}_{2}_pkey" PRIMARY KEY ("{2}");\n'.format(change.tableName, column.name)
                        if column.unique:
                            constraints += 'ALTER TABLE "{0}" ADD CONSTRAINT "{1}_{2}_key" UNIQUE ("{2}");\n'.format(change.tableName, column.name)
                        sql += ';\n'
                        sql += constraints
                
                elif isinstance(change, DropColumns):
                    self.log.info('Dropping Columns')
                    for column in change.columnNames:
                        sql += 'ALTER TABLE "{0}" DROP COLUMN "{1}";\n'.format(change.tableName, column)
                
                else:
                    raise UnknownChangeError('Change {0} of changeset {1} is not a known change!'.format(change, changeSet.__name__))
                
                self.logSQL.info(sql)
                cur.execute(sql);
            
            # changelog
            cur.execute('''INSERT INTO "{0}" (name, datetime) VALUES ('{1}', '{2}');'''.format(
                self.tableChangelog, changeSet.__name__, self.datetime()))
            self.log.info('Successfully processed Changeset')
