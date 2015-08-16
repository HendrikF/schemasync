class column:
    def __init__(self, name, typ, length=None, *, primaryKey=False, null=True, unique=False):
        self.name = name
        self.type = typ
        self.length = length
        self.primaryKey = primaryKey
        self.null = null
        self.unique = unique
