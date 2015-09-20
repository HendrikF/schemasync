from .errors import IntegrityError

class Schemasync:
    def __init__(self, dialect):
        self.dialect = dialect
    
    def process(self, changeSets):
        self.dialect.lock()
        try:
            changeSetsDone = self.dialect.changeSetsDone()
            self.verifyDataIntegrity(changeSets, changeSetsDone)
            for changeSet in self.filterChangeSets(changeSets, changeSetsDone):
                self.dialect.process(changeSet)
        finally:
            self.dialect.release()
    
    def filterChangeSets(self, changeSets, changeSetsDone):
        for changeSet in changeSets:
            if changeSet.__name__ not in changeSetsDone:
                yield changeSet
    
    def verifyDataIntegrity(self, changeSets, changeSetsDone):
        changeSetNames = [changeSet.__name__ for changeSet in changeSets]
        setsProvided = set(changeSetNames)
        setsDone = set(changeSetsDone)
        setsDoneButNotProvided = setsDone - setsProvided
        if len(setsDoneButNotProvided) > 0:
            raise IntegrityError('ChangeSets ({}) only exist in database'.format(', '.join(setsDoneButNotProvided)))
