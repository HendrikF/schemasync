from . import postgresql

dialects = {
    'postgresql': postgresql.postgresql
}

__all__ = [
    'dialects'
]
