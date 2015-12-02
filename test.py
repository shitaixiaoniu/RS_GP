import numpy as np
from scipy.sparse import lil_matrix
a = lil_matrix((3,4))
a[2,1] = 1
a[2,3] = 1
a[2,0] = 5 
a[0,1] = 1

b = [1,2,3]
print a[2,[1,2,3]].toarray()
c= np.multiply(a[2,[1,2,3]],b)
print np.count_nonzero(c)
print c.size
print np.sum(c)
"""
from sklearn.neighbors import NearestNeighbors
import sklearn.metrics.pairwise as smp
import numpy as np

test=np.random.randint(0,5,(50,50))
nbrs = NearestNeighbors(n_neighbors=5, algorithm='brute', metric='cosine').fit(test)
distances, indices = nbrs.kneighbors(test)

x=21   

print distances[x]
for idx,d in enumerate(indices[x]):

    sim2 = smp.cosine_similarity(test[x],test[d])


    print "sklearns cosine similarity would be ", sim2
    print 'sklearns reported distance is', distances[x][idx]
    print 'sklearns if that distance was cosine, the similarity would be: ' ,1- distances[x][idx]
"""
