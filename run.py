from .dialects import dialects
from .changes.changeset import _getAll

def run(connection, dialect='postgresql'):
    dialects[dialect](connection).run(_getAll())
