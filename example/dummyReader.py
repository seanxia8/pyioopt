import core

class event(core.event) :
    

class reader(core.eventReader) :
    def __init__(self) :
        self.name = "dummyReader"
        self.events = [
            core.event(
            

    def addFile(self, fileName) :
        self.filename = fileName
        self.nFiles = 1

    def nFiles(self) :
        return nFiles

    def __getitem__(self, i) :
        
