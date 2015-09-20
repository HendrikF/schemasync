# Schemasync

## Source Control for Databases

*(Just like with [Liquibase](http://www.liquibase.org)...)*

> Schemasync is a python3 library for managing your databases schema along with your source code.
> 
> *Remember, that it is in alpha stadium.*

## How It Looks Like

Schema is managed in **changesets**. Every changeset can contain one or more **changes**. Changesets and changes are defined in Python.

Here is how a changeset with 2 changes looks like:

```python
from schemasync.changes import *
from schemasync.definitions import *

changesets = []

# It is up to you, how you organize your changesets
# My method is a bit hacky :)
changeset = changesets.append

@changeset
def createTablePerson():
    yield CreateTable('person', [
        Column('id', 'auto', primaryKey=True),
        Column('firstname', 'varchar', 200, null=False),
        Column('lastname', 'varchar', 200, null=False),
    ], constraints=[
        UniqueConstraint('name', ('firstname', 'lastname')),
    ])
    yield DropTable('employees')
```

This way you can start schemasync:

```python
import psycopg2 as dbapi
connection = dbapi.connect(host='localhost', database='test', user='test', password='SUPER_$ecret')

from schemasync.Schemasync import Schemasync
from schemasync.dialects.PostgreSQL import PostgreSQL
schemasync = Schemasync(PostgreSQL(dbapi, connection))

schemasync.process(changesets)
```

## Data Integrity

- A changeset should be written in a way, that the database is in a consistent state after each changeset.
- A changeset is either processed completely or - in the case of an error - not at all, which means that the changes are reverted by a rollback of the transaction.
- Every changeset runs in its own **transaction** to prevent the database from an inconsistent state.
- If processing of a changeset failed, the following changesets will be skipped, because they might depend on each other.

## Database Support

At the moment, only PostgreSQL is supported by default, because IMHO it is the best Relational Database Management System.
It is, of course, possible to implement other *Dialect*s.

To do this, you would have to write things like the following, just look at the PostgreSQL implemetation.

```python
# ...
elif isinstance(change, DropColumns):
    for column in change.columnNames:
        sql += 'ALTER TABLE "{0}" DROP COLUMN "{1}";\n'.format(change.tableName, column)
# ...
```

## Change Support

At the moment, only very basic operations are implemented:

- Create Table
- Rename Table
- Drop Table
- Add Columns
- Drop Columns

## License

Schemasync is released under the GNU GPLv3. See `GPLv3.md` for Details.

> Copyright (C) 2015 Hendrik Fritsch
> 
> This program is free software: you can redistribute it and/or modify
> it under the terms of the GNU General Public License as published by
> the Free Software Foundation, either version 3 of the License, or
> (at your option) any later version.
> 
> This program is distributed in the hope that it will be useful,
> but WITHOUT ANY WARRANTY; without even the implied warranty of
> MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
> GNU General Public License for more details.
> 
> You should have received a copy of the GNU General Public License
> along with this program.  If not, see <<http://www.gnu.org/licenses/>>.
