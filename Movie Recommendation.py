#!/usr/bin/env python
# coding: utf-8

# In[8]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sklearn.metrics.pairwise import cosine_similarity
from ast import literal_eval
import ast


# In[9]:


credits_df = pd.read_csv("tmdb_5000_movies.csv")
movies_df = pd.read_csv("tmdb_5000_credits.csv")
print(movies_df.head())


# In[10]:


credits_df.head()


# In[11]:


movies_df.head()


# In[12]:


# Demographic Filtering
C = credits_df["vote_average"].mean()
m = credits_df["vote_count"].quantile(0.9)
print("C: ", C)
print("m: ", m)
new_movies_df = credits_df.copy().loc[credits_df["vote_count"] >= m]
print(new_movies_df.shape)
def weighted_rating(x, C=C, m=m):
    v = x["vote_count"]
    R = x["vote_average"]
    return (v/(v + m) * R) + (m/(v + m) * C)
    new_movies_df["score"] = new_movies_df.apply(weighted_rating, axis=1)
    new_movies_df = new_movies_df.sort_values('score', ascending=False)
    new_movies_df[["title", "vote_count", "vote_average", "score"]].head(10)
    


def plot():
    popularity = movies_df.sort_values("popularity", ascending=False)
    plt.figure(figsize=(12, 6))
    plt.barh(popularity["title"].head(10), popularity["popularity"].head(10), align="center", color="skyblue")
    plt.gca().invert_yaxis()
    plt.title("Top 10 movies")
    plt.xlabel("Popularity")
    plt.show()
    plot()


# In[13]:


# Content-based Filtering
#x = v.fit_transform(credits_df['overview'].values.astype('U'))  ## Even astype(str) would work
print(credits_df["overview"].head(5))
tfidf = TfidfVectorizer(stop_words="english")
credits_df["overview"] = credits_df["overview"].fillna("")
tfidf_matrix = tfidf.fit_transform(credits_df["overview"])
print(tfidf_matrix.shape)


# In[14]:


# Compute similarity
cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
print(cosine_sim.shape)
indices = pd.Series(movies_df.index, index=movies_df["title"]).drop_duplicates()
print(indices.head())


# In[15]:


#implementation
def get_recommendations(title, cosine_sim=cosine_sim):
    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]
    movies_indices = [ind[0] for ind in sim_scores]
    movies = movies_df["title"].iloc[movies_indices]
    return movies


# In[16]:


print("# Content Based Filtering - plot#")
print()
print("Recommendations for The Dark Knight Rises")
print(get_recommendations("The Dark Knight Rises"))
print()
print("Recommendations for Avengers")
print(get_recommendations("The Avengers"))


# In[16]:


def get_director(x):
    for i in x:
        if i["job"] == "Director":
            return i["name"]
    return np.nan
def get_list(x):
    if isinstance(x, list):
        names = [i["name"] for i in x]
        if len(names) > 3:
            names = names[:3]
        return names
    return []


# In[ ]:


def clean_data(x):
    if isinstance(x, list):
        return [str.lower(i.replace(" ", "")) for i in x]
    else:
        if isinstance(x, str):
            return str.lower(x.replace(" ", ""))
        else:
            return ""
features = ['cast', 'keywords', 'director', 'genres']
for feature in features:
    movies_df[feature] = movies_df[feature].apply(clean_data)
def create_soup(x):
    return ' '.join(x['keywords']) + ' ' + ' '.join(x['cast']) + ' ' + x['director'] + ' ' + ' '.join(x['genres'])
movies_df["soup"] = movies_df.apply(create_soup, axis=1)
print(movies_df["soup"].head())


# In[ ]:


count_vectorizer = CountVectorizer(stop_words="english")
count_matrix = count_vectorizer.fit_transform(movies_df["soup"])
print(count_matrix.shape)
cosine_sim2 = cosine_similarity(count_matrix, count_matrix)
print(cosine_sim2.shape)
movies_df = movies_df.reset_index()
indices = pd.Series(movies_df.index, index=movies_df['title'])


# In[ ]:


#Testing
print("# Content Based System - metadata #")
print("Recommendations for The Dark Knight Rises")
print(get_recommendations("The Dark Knight Rises", cosine_sim2))
print()
print("Recommendations for Avengers")
print(get_recommendations("The Avengers", cosine_sim2))

