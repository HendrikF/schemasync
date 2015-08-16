_changesets = []

def changeset(func):
    _changesets.append(func)

def _getAll():
    return _changesets
