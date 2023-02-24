from django.db import connection
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

def getAllNodes():
    cursor = connection.cursor()
    cursor.execute("select id,name,description,x_position,y_position from concept_node;")
    concepts = cursor.fetchall()
    cursor.close()
    connection.close()
    concepts = [list(concept) for concept in concepts]
    return concepts


def getAllConnections():
    cursor = connection.cursor()
    cursor.execute("select id,source_node_id,target_node_id from connection;")
    connections = cursor.fetchall()
    cursor.close()
    connection.close()
    connections = [list(c) for c in connections]
    return connections


def parseConfig():
    with open('/Users/lianyang/Desktop/Projects/starter-projects/Proj1/cv_app/app/.env') as f:
        env_lines = f.read().splitlines()
    d = {}
    for line in env_lines:
        if not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            d[key] = value.strip()
    return d


def extract_keywords(text):
    # tokenize the text into individual words
    tokens = word_tokenize(text)

    # remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word.lower() not in stop_words]

    # Lemmatize the remaining words
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]

    # Identify the most common words and bigrams in the text
    freq_dist = nltk.FreqDist(tokens)
    keywords = []
    for word, count in freq_dist.most_common(3):
        if word not in [',', '.'] and word.lower() not in keywords:
            keywords.append(word.lower())

    return keywords
