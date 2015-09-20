class Dialect:
    tableLock = 'schemasync_lock'
    tableChangelog = 'schemasync_changelog'
    
    def lock(self):
        raise NotImplementedError
    
    def release(self):
        raise NotImplementedError
    
    def changeSetsDone(self):
        raise NotImplementedError
    
    def process(self, changeSet):
        raise NotImplementedError
