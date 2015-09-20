class SchemasyncError(Exception):
    pass

class LockError(SchemasyncError):
    pass

class IntegrityError(SchemasyncError):
    pass

class UnknownChangeError(SchemasyncError, TypeError):
    pass
