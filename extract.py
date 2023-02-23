import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


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
    for word, count in freq_dist.most_common(10):
        if word not in [',', '.'] and word.lower() not in keywords:
            keywords.append(word.lower())

    return keywords


with open('source.txt', 'r') as file:
    content = file.read()

result = extract_keywords(content)
print(result)
