class CreateTable:
    def __init__(self, tableName, columns, *, constraints=[], schemaName=None):
        self.tableName = tableName
        self.columns = columns
        self.constraints = constraints
        self.schemaName = schemaName

class RenameTable:
    def __init__(self, oldName, newName, *, oldSchemaName=None, newSchemaName=None):
        self.oldName = oldName
        self.newName = newName
        self.oldSchemaName = oldSchemaName
        self.newSchemaName = newSchemaName

class DropTable:
    def __init__(self, tableName, *, schemaName=None):
        self.tableName = tableName
        self.schemaName = schemaName

class AddColumns:
    def __init__(self, tableName, columns, *, schemaName=None):
        self.tableName = tableName
        self.columns = columns
        self.schemaName = schemaName

class DropColumns:
    def __init__(self, tableName, columnNames, *, schemaName=None):
        self.tableName = tableName
        self.columnNames = columnNames
        self.schemaName = schemaName

class RenameColumn:
    def __init__(self, tableName, oldColumnName, newColumnName, *, schemaName=None):
        self.tableName = tableName
        self.oldColumnName = oldColumnName
        self.newColumnName = newColumnName
        self.schemaName = schemaName

class CreateSequence:
    def __init__(self, sequenceName, *, schemaName=None, cycle=None, 
            incrementBy=None, maxValue=None, minValue=None, ordered=None, startValue=None):
        self.sequenceName = sequenceName
        self.schemaName = schemaName
        self.cycle = cycle
        self.incrementBy = incrementBy
        self.maxValue = maxValue
        self.minValue = minValue
        self.ordered = ordered
        self.sequenceName = sequenceName
        self.startValue = startValue

class RenameSequence:
    def __init__(self, oldSequenceName, newSequenceName, *, oldSchemaName=None, newSchemaName=None):
        self.oldSequenceName = oldSequenceName
        self.newSequenceName = newSequenceName
        self.oldSchemaName = oldSchemaName
        self.newSchemaName = newSchemaName
