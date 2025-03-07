# Video_Recommendation_System


1. Project overview:

This task is a Video advice gadget designed to offer personalized video pointers to customers. It makes use of a Deep Neural community (DNN) to advise movies for current customers and employs temper-based recommendations for brand new users to cope with the bloodless begin trouble. The machine utilizes sentiment evaluation to decide user temper and suggests films thus.

2. facts Fetching, Preprocessing, and model schooling
information Fetching and Preprocessing
information source: Video facts is loaded from CSV files (Final_DataSet.csv for existing customers and video_dataset_2.csv for brand spanking new users).

Preprocessing Steps:

function Extraction: applicable features which include video id, name, summary, and tags are extracted.

records Normalization: Numerical functions are normalized to improve model performance.

coping with missing Values: lacking textual content fields (e.g., identify, summary, tags) are packed with default values.

categorical Encoding: categorical functions are encoded for version input.

Neural network architecture
Embedding Layers: Used for specific features like consumer identification and video identification.

Dense Layers: more than one dense layers with ReLU activation to study complex styles.

Dropout: added for regularization to prevent overfitting.

Output Layer: Sigmoid activation for predicting interplay ratings.

The model is skilled on user-video interaction facts to are expecting possibilities and propose movies.

three. mood-based totally recommendations for brand spanking new users
for brand spanking new users without interaction history, the device uses temper-based pointers:

Sentiment analysis: Analyzes person-supplied text (e.g., "I experience glad nowadays") the use of Hugging Face's Transformers library to determine mood (effective, neutral, negative).

content material-based totally Filtering: Recommends videos primarily based on metadata (name, summary, tags) matching the user's temper.

popularity-based totally Fallback: indicates trending videos if no mood-based hints are to be had.

4. the use of Postman for API trying out
The device presents a RESTful API built with FastAPI. Postman is used to:

take a look at API endpoints (e.g., /suggest/{user_id}, /recommend_by_mood/{mood_label}).

Debug and validate API responses.

exhibit API functionality in the technical demo.

5. Database Migration
The machine makes use of SQLite for information storage:

Database Schema:

customers: shops consumer information (id, name, introduction timestamp).

video_preferences: stores person-video interactions (person identification, video identity, video title, timestamp).

Migration Scripts: make sure clean database setup and schema updates.


Concusion:
This assignment demonstrates the usage of Deep Neural Networks and sentiment evaluation to build a robust video advice machine. It successfully handles the cold start hassle and presents personalised tips for both present and new customers. As an engineering pupil, this assignment has been a treasured getting to know experience in constructing cease-to-give up machine getting to know systems.



