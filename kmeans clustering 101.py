# Let's start by importing some site packages shall we?
# These packages will assist in webscraping
import requests
from BeautifulSoup import BeautifulSoup
# These packages are for tabular manipulation
import pandas as pd
# These packages are for graphing
import matplotlib.pyplot as plt
# This is how the KMeans Sausage is made
from sklearn.cluster import KMeans
# This is a hack to make sure my IDE will display my Tables!
import sys;
sys.setrecursionlimit(40000)

# Now we'll go ahead and grab some data
# If you are working on a plane and can't get ahold of the interwebs, maybe you want to work from file
fantasy_pros_csv = r'C:\Fantasy\Data\Fantasy Pros\hitters 20170501.csv'
# Here's some webscraping logic to grab data from FantasyPros
pos_type = 'hitters'
url      =   "https://www.fantasypros.com/mlb/stats/{0}.php?range=2017".format(pos_type)
r               = requests.get(url)
soup            = BeautifulSoup(r.content)
table_data      = soup.find("table", { "class" : "table table-bordered table-full table-striped table-hover"})
headers = [header.text for header in table_data.findAll('th')]

# All of our data is in a 'Beautiful Soup' but we think in tables so let's coerce this data into a shape
rows = []
for row in table_data.findAll("tr"):
    cells = row.findAll("td")
    if len(cells) == 19:
        vbr     = cells[0].find(text=True)
        player  = cells[1].find(text=True) # insert logic to change names
        AB      = float(cells[2].find(text=True))
        R       = float(cells[3].find(text=True))
        HR       = float(cells[4].find(text=True))
        RBI      = float(cells[5].find(text=True))
        SB     = float(cells[6].find(text=True))
        AVG    = float(cells[7].find(text=True))
        OBP      = float(cells[8].find(text=True))
        H      = float(cells[9].find(text=True))
        B2      = float(cells[10].find(text=True))
        B3      = float(cells[11].find(text=True))
        BB       = float(cells[12].find(text=True))
        SO      = float(cells[13].find(text=True))
        SLG       = float(cells[14].find(text=True))
        OPS      = float(cells[15].find(text=True))
        Own     = cells[16].find(text=True)
        if vbr != '&nbsp;':
            rows.append([float(vbr), player, AB, R, HR, RBI, SB, AVG, OBP, H, B2, B3, BB, SO, SLG, OPS, float(Own[:-1])/100])

# Great, our Data is in a list of lists: much more pythonic. Let's birth a pandas table!
#df = pd.DataFrame(rows, columns=headers)
#df.to_csv(fantasy_pros_csv, index=False)
df = pd.read_csv(fantasy_pros_csv)

# Unfortunately, most scientific packages in ptyhon don't work with pandas directly. We'll extract an array into numpy with the data that we'll cluster.
X = df[['R','RBI', 'HR', 'SB']].values

# Let's take a look at few variable scatters. These get hard because of the differing distributions amongst stats.
r2rbi = plt.scatter(X[:, 0], X[:, 1], linewidths=0, alpha = 0.2)
#rbi2hr = plt.scatter(X[:, 1], X[:, 2], linewidths=0, alpha = 0.2)
#r2sb = plt.scatter(X[:, 0], X[:, 3], linewidths=0, alpha = 0.2)

# Now it's time for the heavy lifting. RUn that beautiful bean footage! Here's how the clusters get made. 
# I played around with the cluster count and liked what I got with 7.
kmeans = KMeans(n_clusters=7, random_state=0)
kmeans.fit(X)
predict = kmeans.predict(X)

# Let's characterize these clusters a shade to see what we're dealing with.
centroids = kmeans.cluster_centers_
labels = kmeans.labels_
print(centroids)
print(labels)

# I still see things better in tables, so I'll pop the cluster assignments back to the dataframe.
df['Clusters'] = pd.Series(predict, index=df.index)
#fantasy_pros_clusters = r'C:\Fantasy\Data\Fantasy Pros\hitter clusters.csv'
#df.to_csv(fantasy_pros_clusters, index=False)

# That tells us a bit, but we can get more with some graphs. Let's start in 2D graphing the Runs to RBI relationship.
colors = ["k.","r.", "c.","y.", "m.", "g.", "b."]
for i in range(len(X)):
    print("coordinate:",X[i], "label:", labels[i])
    plt.plot(X[i][0], X[i][1], colors[labels[i]], markersize = 10)
cluster2d = plt.scatter(centroids[:, 0],centroids[:, 1], marker = "x", s=150, linewidths = 0, zorder = 10, alpha = 0.2)

# Part of the clustering appeal is that it can handle a lot of dimensions. Indeed, we gave the clustering algorithm 4 dimensions.
# Let's take a look at how these clusters look in 3D by adding the HR totals as the z direction.
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
for i in range(len(X)):
    print("coordinate:",X[i], "label:", labels[i])
    ax.scatter(X[i][0], X[i][1], X[i][2], c = colors[labels[i]][0], linewidths = 0, alpha = 0.5)