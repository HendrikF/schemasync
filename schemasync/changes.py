class CreateTable:
    def __init__(self, tableName, columns, *, constraints=[]):
        self.tableName = tableName
        self.columns = columns
        self.constraints = constraints

class RenameTable:
    def __init__(self, oldName, newName):
        self.oldName = oldName
        self.newName = newName

class DropTable:
    def __init__(self, tableName):
        self.tableName = tableName

class AddColumns:
    def __init__(self, tableName, columns):
        self.tableName = tableName
        self.columns = columns

class DropColumns:
    def __init__(self, tableName, columnNames):
        self.tableName = tableName
        seld.columnNames = columnNames
