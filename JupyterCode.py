#!/usr/bin/env python
# coding: utf-8

# # Data wrangling: *WerateDogs* Twitter Data

# In[ ]:


# importing required libraries
import pandas as pd
import numpy as np
import tweepy
import requests
import re
import json 
import datetime
import os
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')
import seaborn as sns 
from scipy import stats
import warnings
warnings.filterwarnings('ignore')


pd.set_option('display.max_colwidth', -1)


pd.set_option('display.max_columns', None)


pd.set_option('display.float_format', '{:20,.3f}'.format)


# # Gathering Data

# In[2]:


df_twitt = pd.read_csv('twitter-archive-enhanced.csv')


# In[3]:


#downloading image predictions file using request library .
url = 'https://d17h27t6h515a5.cloudfront.net/topher/2017/August/599fd2ad_image-predictions/image-predictions.tsv'
response = requests.get(url)
with open('image-predictions.tsv' , mode = 'wb') as file :
    file.write(response.content)


# In[ ]:


import tweepy
from tweepy import OAuthHandler
import json
from timeit import default_timer as timer

# Query Twitter API for each tweet in the Twitter archive and save JSON in a text file
# These are hidden to comply with Twitter's API terms and conditions
consumer_key = 'HIDDEN'
consumer_secret = 'HIDDEN'
access_token = 'HIDDEN'
access_secret = 'HIDDEN'

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)

api = tweepy.API(auth, wait_on_rate_limit=True)

# NOTE TO STUDENT WITH MOBILE VERIFICATION ISSUES:
# df_1 is a DataFrame with the twitter_archive_enhanced.csv file. You may have to
# change line 17 to match the name of your DataFrame with twitter_archive_enhanced.csv
# NOTE TO REVIEWER: this student had mobile verification issues so the following
# Twitter API code was sent to this student from a Udacity instructor
# Tweet IDs for which to gather additional data via Twitter's API
tweet_ids = df_twitt.tweet_id.values
len(tweet_ids)

# Query Twitter's API for JSON data for each tweet ID in the Twitter archive
count = 0
fails_dict = {}
start = timer()
# Save each tweet's returned JSON as a new line in a .txt file
with open('tweet_json.txt', 'w') as outfile:
    # This loop will likely take 20-30 minutes to run because of Twitter's rate limit
    for tweet_id in tweet_ids:
        count += 1
        print(str(count) + ": " + str(tweet_id))
        try:
            tweet = api.get_status(tweet_id, tweet_mode='extended')
            print("Success")
            json.dump(tweet._json, outfile)
            outfile.write('\n')
        except tweepy.TweepError as e:
            print("Fail")
            fails_dict[tweet_id] = e
            pass
end = timer()
print(end - start)
print(fails_dict)


# In[4]:


# converting tweet-json file into a data list
df_l = []

with open('tweet-json.txt') as file:
    for line in file:
        df_l.append(json.loads(line))


# In[5]:


df_l[0]


# In[6]:


# creating anew dataframe contains retweet_count , id's , favorite_count
tt = pd.DataFrame(df_l , columns = ['retweet_count' , 'id' , 'favorite_count'])


# In[7]:


tt.head(5)


# In[8]:


tt.tail(5)


# In[9]:


# converting the name of 'id' into 'tweet_id'
tt = tt.rename(columns = {'id' : 'tweet_id'})
tt.head(5)


# In[10]:


# saving the dataframe to a csv file
tt.to_csv('tt.csv' , index = False )


# # Data Assessing
# - *visually and programmatically*
# - *documentation at least 8 quality issues and 2 tidness issues*

# Assessing the twitter archieve enhanced

# In[11]:


df_twitt.head()


# In[12]:


df_twitt.info()


# In[13]:


df_twitt[['rating_numerator', 'rating_denominator']].describe()


# In[14]:


df_twitt.sample(20)


# In[15]:


df_twitt[df_twitt.rating_numerator < 10 ].count()[0]


# In[16]:


#check which tweet_id have numerator under 10 
df_twitt[df_twitt.rating_numerator < 10 ].tweet_id.sample(20)


# In[17]:


#getting the text of tweet_id = 745712589599014916
df_twitt.loc[1029 , 'text']


# In[18]:


#checking demonerator 
df_twitt.rating_denominator.describe()

some denominators (min , max) doesn't make sense 
# In[19]:


df_twitt[df_twitt.rating_denominator != 10 ].count()


# In[20]:


df_twitt[df_twitt.rating_denominator == 10 ].count()


# In[21]:


df_twitt[df_twitt.rating_denominator == 0 ].count()[0]


# In[22]:


#checking which this one tweet_id have a 0 rating value
df_twitt[df_twitt.rating_denominator == 0 ].tweet_id


# In[23]:


#getting the tweet of this one
df_twitt.loc[313 , 'text']


# In[24]:


#check samples of the name dogs
df_twitt.name.value_counts()

there is anon meaning names like (a - an - the - .....) !
# Assesing the twitter image predictions 

# In[25]:


t_predect = pd.read_csv('image-predictions.tsv' , sep = '\t')


# In[26]:


t_predect.head()


# In[27]:


t_predect.tail()


# In[28]:


t_predect.info()


# 
# 
# 
# 
# Assessing Data from twitter API

# In[29]:


tt.head()


# In[30]:


tt.tail()


# In[31]:


tt.info()


# Quality and Tidines

# Quality :
# - Removing around 181 retweeted as indicated by retweeted_status_id 
# - Alot of dogs names are invalid like (a , the , a , None)
# - Converting data type of tweet_id into str instead of integer
# - Missing images for id's 
# - Missing values for Columns (doggo, floofer, pupper, puppo)
# - Converting data type of timestamp column into datetime instead of str 
# - Converting data type of The rating_numerator column into type float and we can extracted this column correctly more
# - Removing another values from rating_denominator column except 10

# Tidines :
# - Merging the three data sets in one
# - Combining the columns doggo, puppo, pupper, floofer into a single column
# 

# # Data Cleaning

# first thing before cleaning is taking copy from files

# In[32]:


clean_1 = df_twitt.copy()
clean_2 = tt.copy()
clean_3 = t_predect.copy()


# # Quality issues:

# Define:
# 
# Removing around 181 retweeted as indicated by retweeted_status_id (Quality)

# Code:

# In[33]:


clean_1 = clean_1[clean_1.retweeted_status_id.isnull()]
clean_1.info()


# In[34]:


# removing related columns
clean_1 = clean_1.drop(columns = ['retweeted_status_id','retweeted_status_user_id','retweeted_status_timestamp'])


# Test:

# In[35]:


clean_1.info()


# _____________________________________________________________

# Define:
# 
# Alot of dogs names are invalid like (a , the , a , None) (Quality)

# Code:

# In[36]:


clean_1.name = clean_1.name.replace(regex = ['^[a-z]+','None'],value = np.nan)
# checking numbers of nan values at name column
sum(clean_1.name.isnull())


# In[37]:


#creating a function to extracting name from text column and return Nan if there is no named word
def extracting(text):
    t_list = text.split()
    for word in t_list:
        if word.lower() == 'named' :
            name_index = t_list.index(word) + 1
            return t_list[name_index]
        else:
            pass
    return np.nan


# In[38]:


# np.where for what to do if function true or false
clean_1.name = np.where(clean_1.name.isnull() , clean_1.text.apply(extracting),clean_1.name)


# Test:

# In[39]:


sum(clean_1.name.isnull())


# _________________________________________________________________

# Define:
# 
# Converting data type of tweet_id into str instead of integer (Quality)

# Code:

# In[40]:


# converting data type of tweet_id into str
clean_1.tweet_id = clean_1.tweet_id.astype(str)


# Test:

# In[41]:


clean_1.info()


# ____________________________________________________

# Define:
#     
# Missing images for id's (Quality)

# Code:

# In[42]:


clean_3 = clean_3[clean_3.jpg_url.notnull()]


# Test:

# In[43]:


clean_3.info()


# ________________________________________________________

# Define:
#     
# Missing values for Columns (doggo, floofer, pupper, puppo) (Quality)

# Code:

# In[44]:


dogs_col = ['doggo', 'floofer', 'pupper', 'puppo']

for col in dogs_col:
    clean_1[col] = clean_1[col].replace('None', np.nan)


# Test:

# In[45]:


clean_1.info()


# ________________________________________________________

# Define:
#     
# Converting data type of timestamp column into datetime instead of str (Quality)

# Code:

# In[46]:


clean_1.timestamp = pd.to_datetime(clean_1.timestamp)


# Test:

# In[47]:


clean_1.info()


# ________________________________________________________

# Define:
#     
# Converting data type of The rating_numerator column into type float and we can extracted this column correctly more (Quality)

# Code:

# In[48]:


clean_1[clean_1.text.str.contains(r"(\d+\.\d*\/\d+)")][['text', 'rating_numerator']]


# In[49]:


new_rate = clean_1[clean_1.text.str.contains(r"(\d+\.\d*\/\d+)")]['text'].str.extract(r"(\d+\.\d*(?=\/\d+))")
new_rate


# In[50]:


clean_1.loc[new_rate.index, 'rating_numerator'] = new_rate.values


# In[51]:


clean_1.rating_numerator = clean_1.rating_numerator.astype('float')


# Test:

# In[52]:


clean_1.loc[new_rate.index]


# ________________________________________________________

# Define:
#     
# Removing another values from rating_denominator column except 10 (Quality)

# Code:

# In[53]:


clean_1 = clean_1[clean_1['rating_denominator'] == 10]


# Test:

# In[54]:


clean_1[['rating_numerator', 'rating_denominator']].describe()


# ________________________________________________________

# ________________________________________________________

# # Tidines issues

# Define:
#     
# Merging the three data sets in one (Tidines)

# Code:

# In[55]:


# merging the twitter archive enhanced with the tweet data from twitter API
clean_1 = pd.merge(clean_1 , clean_2.astype(object) , on = 'tweet_id' , how = 'left')
# merging the resulting with tweet image predictions
clean_1 = pd.merge(clean_1 , clean_3.astype(object) , on = 'tweet_id' , how = 'left')


# Test:

# In[56]:


clean_1.info()


# ________________________________________________________

# Define:
#    
# Combining the columns doggo, puppo, pupper, floofer into a single column
# (Tidines)

# Code:

# In[57]:


# extract dog stage from text column to the new dog_stage column:
clean_1['dog_stage'] = clean_1['text'].str.extract('(doggo|floofer|pupper|puppo)')
clean_1.head(5)


# Test:

# In[58]:


clean_1.dog_stage.value_counts()


# ________________________________________________________

# ________________________________________________________

# # Data Analysis and Visualization:

# In[59]:


#sorting file 'twitter-archive-enhanced.csv' after cleaning
clean_1.to_csv('twitter_archive_master.csv')


# In[60]:


#dog stages percentages
stage_df = clean_1.dog_stage.value_counts()
stage_df


# In[61]:


# creating a pie chart for dog stages
plt.pie(stage_df , 
       labels = ['Pupper' , 'Doggo' , 'Puppo' ,'Floofer'] ,
       shadow = True ,
       explode = (0.1 , 0.2 , 0.2 , 0.3));
plt.title('Dog stages Percentage');
plt.axis('equal');


# We see that the 'Pupper' has the highest percentage 
# and 'Floofer' has the lowest percentage 

# ________________________________________________________

# In[62]:


# Getting the relation between clean_2.retweet_count and clean_2.favorite_count
plt.scatter(clean_2.retweet_count ,clean_2.favorite_count );
plt.title("Relationship between clean_2.retweet_count and clean_2.favorite_count");
plt.xlabel("Retweet_count");
plt.ylabel("Favorite_count");


# In[63]:


rating = clean_1.rating_numerator.value_counts()

x = rating.index
y = rating.values
fig, ax = plt.subplots(figsize=(16, 6))
g = sns.barplot(x, y, palette='Blues_d', ax=ax)
ax.set(xlabel='Ratings', ylabel='Frequency', title='Ratings frequency')
plt.show()


# In[ ]:




