# Let's start by importing some site packages shall we?
# These packages will assist in webscraping
import requests
from BeautifulSoup import BeautifulSoup
# These packages are for tabular manipulation
import pandas as pd
import numpy as np
# These packages are for graphing
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
# This is how the KMeans Sausage is made
from sklearn.cluster import KMeans
# This is a hack to make sure my IDE will display my Tables!
import sys;
sys.setrecursionlimit(40000)

# Now we'll go ahead and grab some data
# Here's some webscraping logic to grab data from FantasyPros
pos_type = 'pit'
url      =   "http://www.fangraphs.com/leaders.aspx?pos=all&stats={0}&lg=all&qual=y&type=8&season=2017&month=0&season1=2017&ind=0&team=0&rost=0&age=0&filter=&players=0&page=1_1000".format(pos_type)
r               = requests.get(url)
soup            = BeautifulSoup(r.content)
table_data      = soup.find("table", { "class" : "rgMasterTable"})      
            
headers = [header.text for header in table_data.findAll('th')]

# All of our data is in a 'Beautiful Soup' but we think in tables so let's coerce this data into a shape
rows = []
for row in table_data.findAll("tr"):
    cells = row.findAll("td")
    if len(cells) == 20:
        Num   = cells[0].find(text=True)
        Name  = cells[1].find(text=True)
        Team  = cells[2].find(text=True) 
        W     = float(cells[3].find(text=True))
        L     = float(cells[4].find(text=True))
        SV    = float(cells[5].find(text=True))
        G     = float(cells[6].find(text=True))
        GS    = float(cells[7].find(text=True))
        IP    = float(cells[8].find(text=True))
        K9    = float(cells[9].find(text=True))
        BB9   = float(cells[10].find(text=True))
        HR9   = float(cells[11].find(text=True))
        BABIP = float(cells[12].find(text=True))
        LOB   = float(cells[13].find(text=True)[:-2])
        GB    = float(cells[14].find(text=True)[:-2])
        HRFB  = float(cells[15].find(text=True)[:-2])
        ERA   = float(cells[16].find(text=True))
        FIP   = float(cells[17].find(text=True))
        xFIP  = float(cells[18].find(text=True))
        WAR   = float(cells[19].find(text=True))
        rows.append([float(Num), Name, Team, W, L, SV, G, GS, IP, K9, BB9, HR9, BABIP, LOB, GB, HRFB, ERA, FIP, xFIP, WAR])

# Great, our Data is in a list of lists: much more pythonic. Let's birth a pandas table!
df = pd.DataFrame(rows, columns=headers)

# Time for some spring cleaning
df['Rem'] = df['IP']%1*3.33
df['IP'] = df['IP'].apply(np.floor)
df['IP'] = df['IP'] + df['Rem']
df.drop('Rem', axis=1, inplace=True)

# Unfortunately, most scientific packages in ptyhon don't work with pandas directly. We'll extract an array into numpy with the data that we'll cluster.
X = df[['K/9','BB/9', 'FIP']].values

# Let's take a look at few variable scatters. These get hard because of the differing distributions amongst stats.
fig = plt.figure()
k2fip = fig.add_subplot(111)
k2fip.scatter(X[:, 0], X[:, 2], linewidths=0, alpha = 0.2)
fig
fig = plt.figure()
bb2fip = fig.add_subplot(111)
bb2fip.scatter(X[:, 1], X[:, 2], linewidths=0, alpha = 0.2)
fig
fig = plt.figure()
bb2k = fig.add_subplot(111)
bb2k.scatter(X[:, 1], X[:, 0], linewidths=0, alpha = 0.2)
fig

# Now it's time for the heavy lifting. Run that beautiful bean footage! Here's how the clusters get made. 
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

# That tells us a bit, but we can get more with some graphs. Let's start in 2D graphing the BB/9 to FIP relationship.
colors = ["k.","r.", "c.","y.", "m.", "g.", "b."]
fig = plt.figure()
clusters2d = fig.add_subplot(111)
for i in range(len(X)):
#    print("coordinate:",X[i], "label:", labels[i])
    clusters2d.plot(X[i][1], X[i][2], colors[labels[i]], markersize = 10)
clusters2d.scatter(centroids[:, 1],centroids[:, 2], marker = "x")

# Part of the clustering appeal is that it can handle a lot of dimensions. Indeed, we gave the clustering algorithm 3 dimensions.
# Let's take a look at how these clusters look in 3D by adding the K/9 totals as the z direction.
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
for i in range(len(X)):
#    print("coordinate:",X[i], "label:", labels[i])
    ax.scatter(X[i][0], X[i][1], X[i][2], c = colors[labels[i]][0], linewidths = 0, alpha = 0.3)
fig

# Now it's time to finalize that last figure with some labels.
# Let's pick a few interesting dudes
dudes = [['Dan Straily','left'],
         ['Ubaldo Jimenez', 'left'],
         ['Dallas Keuchel', 'right'],
         ['Robbie Ray','left'],
         ['Jordan Zimmermann','right'],
         ['Clayton Kershaw','left'],
         ['Mike Leake','right']]

# We'll need to figure out which points are for which dudes and lableing them on the figure
for dude in dudes:
    dude_name = dude[0]
    wheredude = int(df.loc[df['Name'] == dude_name].iloc[0][0]-1)
    print wheredude
    ax.text(X[wheredude][0],X[wheredude][1],X[wheredude][2],dude_name,color=colors[labels[wheredude]][0],ha=dude[1],size=10)

# Lastly, let's add some labels to each axis
ax.set_xlim(0, 15)
ax.set_ylim(0, 8)
ax.set_zlim(0, 8)
ax.set_xlabel('K/9')
ax.set_zlabel('FIP')
ax.set_ylabel('BB/9', linespacing=3.1)

fig
