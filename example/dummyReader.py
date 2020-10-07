from pyioopt import reader, dataModel, geometry

import numpy as np

class dummyEvent(dataModel.event) :
    def __init__(self, hits, eventNumber, runNumber) :
        self.hits = np.array(hits)
        self.hits.flags.writeable = False

        self.runNumber = runNumber
        self.eventNumber = eventNumber
        
    def __getitem__(self, key) :
        return self.hits.__getitem__(key)

    def __len__(self) :
        return self.hits.__len__()

    def datetime(self) :
        return 0

    def eventNumber(self) :
        return eventNumber

    def runNumber(self) :
        return runNumber
        
class dummyReader(reader.reader) :
    def __init__(self) :
        self.name = "dummyReader"
        self.nFiles = 0
        self.nEvents = 0
        self.filenames = []
        self.eventsPerFile = []
        self.eventsPerFileCumulative = []

    def addFile(self, fileName) :
        self.filenames.append(fileName)
        self.nFiles += 1

        with open(fileName, "r") as f :
            nEventsThisFile = sum([1 for line in f if "event" in line])

        self.eventsPerFile.append(nEventsThisFile)
        if self.nFiles == 1 :
            self.eventsPerFileCumulative.append(nEventsThisFile)
        else :
            self.eventsPerFileCumulative.append(self.eventsPerFileCumulative[-1]+nEventsThisFile)

        self.nEvents += nEventsThisFile

    def __len__(self) :
        return self.nEvents
    
    def __getitem__(self, i) :
        if i > self.nEvents :
            raise IndexError('{0} event {1} is out of range. Number of events in loaded files: {2}'.format(self.name, i, self.nEvents))

        indexOfFileToRead = np.digitize(i, self.eventsPerFileCumulative)
        if indexOfFileToRead == 0 :
            indexOfEventToRead = i
        else :
            indexOfEventToRead = i - self.eventsPerFileCumulative[indexOfFileToRead-1]

        hits = []
        with open(self.filenames[indexOfFileToRead]) as f :
            inEvent = False
            for line in f :
                if "event {0}".format(indexOfEventToRead+1) in line :
                    break

                if "event {0}".format(indexOfEventToRead) in line :
                    inEvent = True
                    continue
                
                if inEvent :
                    lineSplit = line.split()
                    hits.append( dataModel.hit( int(lineSplit[0]), float(lineSplit[1]), float(lineSplit[2])))

        return dummyEvent(hits,  indexOfEventToRead, indexOfFileToRead)
                             
        
