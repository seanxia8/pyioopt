import wcsim_reader

import numpy as np
import matplotlib.pyplot as plt

rd = wcsim_reader.Reader()
print("Initialized reader")

rd.addFile("/Users/cvilela/WCML/TrainingSampleProductionWCSim/wcsim.root")

top = rd.geometry.mask[0]
barrel = rd.geometry.mask[1]
bottom = rd.geometry.mask[2]

print(len(rd))

for iev, event in enumerate(rd) :
    print("EVENT {0}".format(iev))
    for isub, sub in enumerate(event) :
        print ("SUB-EVENT {0}".format(isub))
        print (sub.hits())

        thisTop_q = np.copy(top).astype(float)
        thisTop_t = np.copy(top).astype(float)

        thisBarrel_q = np.copy(barrel).astype(float)
        thisBarrel_t = np.copy(barrel).astype(float)

        thisBottom_q = np.copy(bottom).astype(float)
        thisBottom_t = np.copy(bottom).astype(float)

        for hit in sub.hits() :
            if rd.geometry.pmts()["location"][hit["PMT_number"]-1] == 0 :
                thisTop_q[rd.geometry.pmts()["column"][hit["PMT_number"]-1], rd.geometry.pmts()["row"][hit["PMT_number"]-1]] = hit['q']
                thisTop_t[rd.geometry.pmts()["column"][hit["PMT_number"]-1], rd.geometry.pmts()["row"][hit["PMT_number"]-1]] = hit['t']
            elif rd.geometry.pmts()["location"][hit["PMT_number"]-1] == 1 :
                thisBarrel_q[rd.geometry.pmts()["column"][hit["PMT_number"]-1], rd.geometry.pmts()["row"][hit["PMT_number"]-1]] = hit['q']
                thisBarrel_t[rd.geometry.pmts()["column"][hit["PMT_number"]-1], rd.geometry.pmts()["row"][hit["PMT_number"]-1]] = hit['t']
            elif rd.geometry.pmts()["location"][hit["PMT_number"]-1] == 2 :
                thisBottom_q[rd.geometry.pmts()["column"][hit["PMT_number"]-1], rd.geometry.pmts()["row"][hit["PMT_number"]-1]] = hit['q']
                thisBottom_t[rd.geometry.pmts()["column"][hit["PMT_number"]-1], rd.geometry.pmts()["row"][hit["PMT_number"]-1]] = hit['t']
        plt.figure()
        plt.imshow(thisTop_q)
        plt.figure()
        plt.imshow(thisTop_t)
        plt.figure()
        plt.imshow(thisBarrel_q)
        plt.figure()
        plt.imshow(thisBarrel_t)
        plt.figure()
        plt.imshow(thisBottom_q)
        plt.figure()
        plt.imshow(thisBottom_t)
        plt.show()

        del thisTop_q, thisTop_t, thisBarrel_q, thisBarrel_t, thisBottom_q, thisBottom_t
