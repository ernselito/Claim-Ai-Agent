---
layout: single
title: "Multi-faceted Movie Recommendation System"
excerpt: " "
date: 2025-01-03
read_time: true
comments: true
share: true
related: true
header:
  overlay_color: "#000"
  overlay_filter: "0.5"
  overlay_image: "/assets/images/ml-project-banner.jpg"
  caption: "Exploring prediction with Random Forest"
class: wide
---

#### 1. Problem Statement

I recognize that the digital entertainment landscape is saturated with content, creating a "paradox of choice" that often overwhelms users. I designed this project to directly address the critical challenge of content discovery by building a sophisticated, multi-faceted movie recommendation system. My goal was to move beyond simple popularity rankings and create an engine that delivers personalized, context-aware, and high-quality movie suggestions through a variety of data-driven techniques.


#### 2. Project Objectives

My primary objective was to build a robust engine capable of generating meaningful recommendations through three distinct, yet complementary, approaches:

- Demographic Filtering: I implemented this to provide a baseline for "generally popular" and "highly-rated" movies to all users, segmented by genre.
- Content-Based Filtering: I designed a system to recommend movies similar to a given title based on its intrinsic features, such as plot, cast, crew, and keywords.
- Collaborative Filtering: I built a model to predict a user's preference by analyzing patterns from the collective ratings of all users.
- Hybrid Model: Finally, I combined the strengths of content-based and collaborative filtering to deliver superior, personalized recommendations that account for both movie similarity and individual user taste.

#### 3. Methodology & Technical Approach

I managed the project through a structured, end-to-end pipeline, starting with data acquisition and preprocessing. I sourced my data from Kaggle's The Movies Dataset, specifically working with movies_metadata.csv, credits.csv, keywords.csv, ratings_small.csv, and links_small.csv. My preprocessing involved cleaning the data by handling missing values, parsing complex nested JSON fields for genres, cast, crew, and keywords, converting data types for consistency, and finally merging all the datasets into a single, unified dataframe for analysis.

**b. Demographic Filtering (Genre & Popularity):**

To establish a baseline for "generally popular" movies, I developed a demographic filtering system. I implemented IMDB's weighted rating formula to fairly score movies, balancing their average rating (R) against the total number of votes (v) to ensure statistical significance. I then engineered a function that leverages this formula to dynamically generate ranked lists of the top movies for any genre a user selects.



**c. Content-Based Filtering:**
a. Content-Based Filtering:
To recommend movies based on their intrinsic qualities, I developed two content-based models. First, I engineered a plot-based system using TF-IDF Vectorization on movie overviews and taglines to measure textual similarity. To create a more nuanced system, I built an enhanced metadata model by creating a feature "soup" from the top-billed cast, director, and keywords. After processing these keywords through stemming and relevance filtering, I applied Count Vectorization to build a powerful similarity matrix. I then encapsulated this logic into a function that returns a list of the most similar movies for any given title.

b. Collaborative Filtering (Model-Based):
To incorporate user behavior into the recommendations, I built a collaborative filtering system. I implemented the Singular Value Decomposition (SVD) algorithm using the Surprise library. After training the model on the ratings_small dataset, I rigorously validated its performance through 5-fold cross-validation, achieving a strong RMSE of ~0.897, confirming its predictive power. The final model is capable of accurately predicting how a specific user would rate any movie in the database.

**e. Hybrid Recommendation Engine:**

I developed a core function that synergizes the content-based and collaborative methods.
For a given user and movie title, the engine I built:

Uses my content-based model to find a list of similar movies.
Uses my trained SVD model to predict that specific user's rating for each of these similar movies.
Ranks the final list by these predicted ratings and returns the top 10 personalized recommendations.

#### 4. Key Results & Outputs

- Demographic System: 
I validated this system by having it generate accurate lists of top-rated films like Inception and The Dark Knight, as well as curated genre charts, such as ranking Forrest Gump among the top Romance films.
- Content-Based System:
The effectiveness of my model was clear when querying The Dark Knight returned a highly relevant list including direct sequels like The Dark Knight Rises and thematically similar films from the same director, like The Prestige.
- Hybrid System:
The power of my integrated approach was proven when, for a specific user and the movie Avatar, the engine delivered a personalized list of sci-fi/action classics like Aliens and Terminator 2, which the SVD model predicted that particular user would rate highly.

#### 5. Technologies Used
- Programming Language: Python
- Libraries & Frameworks: I applied Pandas, NumPy, Scikit-learn, Surprise (SVD), and NLTK to handle everything from data processing to model deployment.
- Core Techniques: I successfully implemented techniques like TF-IDF Vectorization, Cosine Similarity, and Matrix Factorization (SVD) to power the different recommendation models.


#### 6. Conclusion

In this project, I demonstrated my comprehensive understanding of modern recommendation system paradigms. By implementing and integrating Demographic, Content-Based, Collaborative, and Hybrid techniques, I built a powerful and versatile movie recommendation engine. This system effectively addresses the initial problem of content discovery, as it is capable of serving both general trending content and deeply personalized suggestions, thereby significantly enhancing the user experience on any movie-based platform.

---
