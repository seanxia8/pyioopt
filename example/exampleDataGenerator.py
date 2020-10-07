import scipy.stats

nEvsMu = [100, 150]
nHitsMu = [1000, 500]
nPMTs = 1000
qMean = [10, 20]
qSigma = [1., 3.]
tMean = [5., 7.]
tSigma = [0.5, 0.5]

for iFile in range(len(nEvsMu)) :
    with open("exampleData_{0}.dat".format(iFile), "w") as f :
        for iev in range(scipy.stats.poisson.rvs(nEvsMu[iFile])) :
            f.write('event {0}\n'.format(iev))
            for ihit in range(scipy.stats.poisson.rvs(nHitsMu[iFile])) :
                f.write('{0} {1} {2}\n'.format(scipy.stats.randint.rvs(low = 0, high = nPMTs),
                                             scipy.stats.norm.rvs(loc = qMean[iFile], scale = qSigma[iFile]),
                                             scipy.stats.norm.rvs(loc = tMean[iFile], scale = tSigma[iFile])))

