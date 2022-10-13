#!/usr/bin/python

# T2G: Twitter-to-Gephi converter, Python edition v 0.l (05/14/13)
# This script converts user mentions in tweets into a format capable of being imported into Gephi (https://gephi.org/), a social network visualization platform. It was written and tested under Python 2.7.3, so YMMV under different installations.
# To use it, begin by creating an input CSV file consisting of two columns: the first (leftmost) containing the usernames of the tweet authors, and the second containing their tweets. Each author username must have a corresponding tweet next to it. Move this file into the working directory of your choice (if using the interpreter this is usually the file where your Python binary lives). After executing T2G, type the name of your input file exactly (including the extension) and it should do its job. The output file should import into Gephi as a directed graph in which ties extend from authors to mentioned users.
# Please report all bugs and unexpected behavior to deen@dfreelon.org.

import csv
import re
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from community import community_louvain
import netgraph
import pandas as pd
from scipy.spatial.distance import pdist
import itertools
from collections import Counter

###code to read the csv file containing the username and their tweets and produce a dataframe showing the tweetauthor and the mentions only
t_list = []
with open('mentdf.csv', errors="replace") as csvfile:    #Reads the csv that contains the usernames and their respective tweets
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
        t_list.append(row)
g_src = [t[0].lower() for t in t_list]  # fills in the list g_src with the names of tweeting users
g_tmp = [' ' + t[1] + ' ' for t in t_list]  # adds 1 space to beginning and end of each tweet
g_tmp = [t.split('@') for t in g_tmp]  # splits each tweet along @s
g_trg = [[t[:re.search('[^A-Za-z0-9_]', t).start()].lower().strip() for t in chunk] for chunk in
         g_tmp]  # strips out everything after the @ sign and trailing colons, leaving (hopefully) a list of usernames

for line in g_trg:
    if len(line) > 1 and line[0] == '':  # removes blank entries from lines, mentioning at least one name
        del line[0]

final = []
i = 0
for list in g_trg:  # creates final output list
    for name in list:
        final.append(g_src[i] + ',' + name + "\n")
    i += 1

for row in final:
    print(row)
edge=pd.DataFrame(final) #stores the "final" list into a dataframe called "edge:
cin=edge.values.tolist()
print(cin)
###############################################################


####Split the username to 2 columns , source and destination in a dataframe###
edge.to_csv('bigtweets', header=['source']) #converts the final list of username-mentions pair to a csv file named bigtweets'
cov= pd.read_csv('bigtweets')
new_df = cov['source'].str.split(',',expand=True)
new_df.columns=['source', 'destination']
new_df['destination'] = new_df['destination'].str.replace('\n', '')
###############################################################

#creates a pair in one column,in this format tweeetauthor-mention
pov= pd.read_csv('bigtweets')
new_df1 = pov['source'].str.replace(',','-')
new_df1=new_df1.str.replace('\n','')
new_df1.columns=['source']
###############################################################

###Creates a dataframe showing the source-destination pair and the number of edges between the nodes
new_df1= pd.DataFrame(new_df1)
print(new_df1)
sur= new_df1['source'].value_counts()
fur=pd.DataFrame(sur) #shows the amount of times a particular pair appears in the dataframe indicating thir frequency of relation on twitter
modified = fur.reset_index()
modified.columns=['source', 'noOfEdges'] #seperates the table into source and noOfEdges
print(fur)
print(modified)
###############################################################

###Draws a Directed Graph from the new_df dataframe and shows the edges between source and destination
G = nx.from_pandas_edgelist(new_df,'source', 'destination', create_using=nx.DiGraph())
#netgraph.draw(G, with_labels=True)
#nx.draw(G, pos=nx.spring_layout(G), with_labels=True)
plt.show() #shows the graph
G_sorted = pd.DataFrame(sorted(G.in_degree, key=lambda x: x[1], reverse=True))
G_sorted.columns = ['nconst','degree'] #shows the user and the degree of its nodes
print(G_sorted.head())
###############################################################

###############################################################

###Additional Graph settings
pos = nx.spring_layout(G)
f, ax = plt.subplots(figsize=(10, 10))
plt.style.use('ggplot')
#cc = nx.betweenness_centrality(G2)
nodes = nx.draw_networkx_nodes(G, pos,
                               cmap=plt.cm.Set1,
                               alpha=0.8)
nodes.set_edgecolor('k')
nx.draw_networkx_labels(G, pos, font_size=8)
nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.2)
plt.show()
#plt.savefig('twitterFollowersbig.png')
###############################################################

###############################################################
c=0
n=1
#print(G_tmp.nodes)
list1=[]
for i in G.nodes:
    list1.append(i)
print(list1) #add all the nodes(twitter usernames) in the graph to a list

#print(str(list1[0]))
# print(nx.shortest_path(G_tmp,str(list1[0+1]), str(list1[6])))
###############################################################

###Find the network Metrics, such as shortest path and Edge Weight
l=[]
d=[]
s=[]
for items in list1:
    for items1 in list1:
        if items1 != items and items1!='':
            print(items+"-"+items1) #diplays a node pair
            string= items+"-"+items1
            l.append(string)
        if ((nx.has_path(G,items, items1)) and (len((nx.shortest_path(G,items,items1)))>1)):
            print(nx.shortest_path(G,items, items1)) #find the shortest path between the node pair
            weight = G.number_of_edges(u=items, v=items1)
            s.append(weight)
            store=len((nx.shortest_path(G,items,items1)))
            d.append(store)

s1=pd.Series(l, name='source') #saves the node pair in the source column
s2=pd.Series(d, name='Spath') #saves the shortest path in the Spath column
s3=pd.Series(s, name='edgeW') #saves the edge weight in the edgeW column
plist=pd.concat([s1,s2,s3], axis=1) #combine the 3 series declared above to a dataframe
print(plist)
###############################################################

###A merged database of Fov and Plist
fov=pd.merge(plist,modified,on='source', how='inner')#merge the fov dataframe and the plist dataframe
# based on the 'source' column, sice they share the same source column
fov[['from','to']]=fov.source.str.split('-', expand=True) #create two seperate columns from the
# source column, to differentiate the sender and the receiver
print(fov.to_string())
###############################################################

##Normalize
can=pd.read_csv('fromwebsite.csv') #read the csv file that contains the user registration entries
can.columns=['LName','FnameAge','Sex','Age', 'TwitterU']
username=can["TwitterU"] #store only the twitter username column in the variable "username"
print(can)
can_age_normalized=(can['Age']-can['Age'].min())/(can['Age'].max()-can['Age'].min()) #normalize the Age column
###############################################################

###create a new Dataframe containing the normalized age and the twitter username
can_age_normalized.columns=['index','N_Age']
can_age_normalized=pd.DataFrame(can_age_normalized)
can_age_normalized=can_age_normalized.join(username)
can_age_normalized.set_index('TwitterU', inplace=True) #set the twitterusername as index
print(can_age_normalized)
###############################################################

###finding the euclidean distances between the ages of each user
data = can_age_normalized.values #store the N_Age in the data variable
d = pd.DataFrame(itertools.combinations(can_age_normalized.index, 2), columns=['from','to']) #using the
# intertool to iterate over a pair of
# usernames and their respective age values and finding the euclidean distance between their ages
d['dist'] = pdist(data, 'euclid') #store the euclidean distance of their ages into a new column 'dist'
###############################################################

###solve the issue of from-to != to-from
d['from2']=d['to']
d['to2']=d['from']
f=d[['from2','to2','dist']]
d= d[['from','to','dist']]
f.columns=['from','to','dist']
to_fro=d.append(f,ignore_index=True)
print(to_fro)
###############################################################

###final dataframe
final=fov.merge(to_fro,how='inner',left_on=['from','to'],right_on=['from','to'])#merge the fov dataframe
# with to_fro dataframe
# removing duplicates and leaving only the user items that appear on the two dataframes
final['Mean']=(final["Spath"]+final["dist"]+(1/final['noOfEdges']))/3 #finding the
# mean between our
# network metrics as the
# final value for our collaborative filtering
print(final.to_string())
#final.to_csv('oshlacopy.csv')
###############################################################
var='mannyconcepts'
reccomend=final.loc[final['from']==var]
print(reccomend)
result= reccomend[reccomend['Mean']==reccomend['Mean'].min()]

print(result)
print(result['to'])

# plist.to_csv('shortestpath1.csv')
# #
# # tb['souce']=l
# # tb['store']=d
# #tb=pd.DataFrame(np.column_stack([l,d]),columns=['source-destination','shortestpath'])
# #print(tb.head())
#
#
#
# # if nx.has_path(G_tmp,"amoodaniel_", "mannyconcepts"):
# #     print(nx.shortest_path(G_tmp, "amoodaniel_", "enilobs"))
# #
# #
# # print(new_df)
#
# #df['Grade'] = df['Grade'].str.replace('%', '')
#
#
#
