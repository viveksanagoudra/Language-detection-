from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
import scipy
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import normalize
from sklearn.naive_bayes import MultinomialNB
import re
from collections import Counter

app = Flask(__name__)

# Load dataset
raw = pd.read_csv(r"C:\Users\vivek\Documents\MINI_PROJECT[1]\MINI PROJECT\templates\dataset.csv")

# Split dataset
X = raw['Text']
y = raw['language']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Extract Unigrams
unigramVectorizer = CountVectorizer(analyzer='char', ngram_range=(1,1))
X_unigram_train_raw = unigramVectorizer.fit_transform(X_train)
X_unigram_test_raw = unigramVectorizer.transform(X_test)
unigramFeatures = unigramVectorizer.get_feature_names_out()

def train_lang_dict(X_raw_counts, y_train):
    lang_dict = {}
    for i in range(len(y_train)):
        lang = y_train[i]
        v = np.array(X_raw_counts[i])
        if lang not in lang_dict:
            lang_dict[lang] = v
        else:
            lang_dict[lang] += v
    for lang in lang_dict:
        v = lang_dict[lang]
        lang_dict[lang] = v / np.sum(v)
    return lang_dict

language_dict_unigram = train_lang_dict(X_unigram_train_raw.toarray(), y_train.values)

# Extract top 1% Uni- & Bi-Grams
top1PrecentMixtureVectorizer = CountVectorizer(analyzer='char', ngram_range=(1,2), min_df=1e-2)
X_top1Percent_train_raw = top1PrecentMixtureVectorizer.fit_transform(X_train)
X_top1Percent_test_raw = top1PrecentMixtureVectorizer.transform(X_test)

language_dict_top1Percent = train_lang_dict(X_top1Percent_train_raw.toarray(), y_train.values)
top1PercentFeatures = top1PrecentMixtureVectorizer.get_feature_names_out()

languages = list(language_dict_top1Percent.keys())
clf = MultinomialNB()

def getRelevantGramsPerLanguage(features, language_dict, top=50):
    relevantGramsPerLanguage = {}
    for lang in languages:
        chars = []
        relevantGramsPerLanguage[lang] = chars
        v = language_dict[lang]
        sortIndex = (-v).argsort()[:top]
        for i in range(len(sortIndex)):
            chars.append(features[sortIndex[i]])
    return relevantGramsPerLanguage

top50PerLanguage_dict = getRelevantGramsPerLanguage(top1PercentFeatures, language_dict_top1Percent)
allTop50 = []
for lang in top50PerLanguage_dict:
    allTop50 += set(top50PerLanguage_dict[lang])
top50 = list(set(allTop50))

def getRelevantColumnIndices(allFeatures, selectedFeatures):
    relevantColumns = []
    for feature in selectedFeatures:
        relevantColumns = np.append(relevantColumns, np.where(allFeatures == feature))
    return relevantColumns.astype(int)

relevantColumnIndices = getRelevantColumnIndices(np.array(top1PercentFeatures), top50)
X_top50_train_raw = np.array(X_top1Percent_train_raw.toarray()[:, relevantColumnIndices])
X_top50_test_raw = X_top1Percent_test_raw.toarray()[:, relevantColumnIndices]

def toNumpyArray(data):
    data_type = type(data)
    if data_type == np.ndarray:
        return data
    elif data_type == list:
        return np.array(data)
    elif data_type == scipy.sparse.csr.csr_matrix:
        return data.toarray()
    return None

def normalizeData(train, test):
    train_result = normalize(train, norm='l2', axis=1, copy=True, return_norm=False)
    test_result = normalize(test, norm='l2', axis=1, copy=True, return_norm=False)
    return train_result, test_result

def applyNaiveBayes(X_train, y_train, X_test):
    trainArray = toNumpyArray(X_train)
    testArray = toNumpyArray(X_test)
    clf.fit(trainArray, y_train)
    y_predict = clf.predict(testArray)
    return y_predict

# Normalize data and fit classifier
X_top50_train, X_top50_test = normalizeData(X_top50_train_raw, X_top50_test_raw)
clf.fit(X_top50_train, y_train)

# Function to predict language of each word in the input text
def predict_language_percentages(text):
    words = re.findall(r'\b\w+\b', text)
    words_transformed = top1PrecentMixtureVectorizer.transform(words)
    words_relevant = words_transformed[:, relevantColumnIndices]
    words_normalized = normalize(words_relevant, norm='l2', axis=1, copy=True, return_norm=False)
    predicted_languages = clf.predict(words_normalized)
    language_counts = Counter(predicted_languages)
    total_words = len(words)
    language_percentages = {lang: round((count / total_words) * 100, 3) for lang, count in language_counts.items()}
    return language_percentages

# Function to predict language from user input
def predict_language(text):
    text_transformed = top1PrecentMixtureVectorizer.transform([text])
    text_relevant = text_transformed[:, relevantColumnIndices]
    text_normalized = normalize(text_relevant, norm='l2', axis=1, copy=True, return_norm=False)
    predicted_language = clf.predict(text_normalized)
    if predicted_language[0] not in languages:
        return 'Language not found'
    return predicted_language[0]

@app.route('/')
def index():
    return render_template('page.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    text = data.get('text', '')
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    language = predict_language(text)
    if language == 'Language not found':
        return jsonify({'error': 'Language not found'}), 404
    return jsonify({'language': language})

@app.route('/predict_percentages', methods=['POST'])
def predict_percentages():
    data = request.get_json()
    text = data.get('text', '')
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    percentages = predict_language_percentages(text)
    return jsonify(percentages)

if __name__ == '__main__':
    app.run(debug=True)
