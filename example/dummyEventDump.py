import dummyReader

rd = dummyReader.dummyReader()

rd.addFile("exampleData_0.dat")

print("Number of events in file 0: {0}".format(len(rd)))

rd.addFile("exampleData_1.dat")

print("Number of events in file 0 and 1: {0}".format(len(rd)))

for i, ev in enumerate(rd) :
    print("Event number {0}. Number of hits: {1}".format(i, len(ev)))
    for iHit, hit in enumerate(ev) :
        print("     Hit {0}, q={1}, t={2}".format(iHit, hit.q, hit.t))
