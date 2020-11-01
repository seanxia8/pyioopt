import wcsimReader

rd = wcsimReader.wcsimReader()
print("Initialized reader")

rd.addFile("/Users/cvilela/WCML/TrainingSampleProductionWCSim/wcsim.root")

print(len(rd))

for iev, event in enumerate(rd) :
    print("EVENT {0}".format(iev))
    for isub, sub in enumerate(event) :
        print ("SUB-EVENT {0}".format(isub))
        print (sub.hits())
