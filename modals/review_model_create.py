# -*- coding: utf-8 -*-

#!wget "https://raw.githubusercontent.com/kishan0725/AJAX-Movie-Recommendation-System-with-Sentiment-Analysis/master/datasets/reviews.txt"

import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
import string
import joblib

#scikit learn modules 
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.metrics import confusion_matrix
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score,accuracy_score

#nlp modules
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer
nltk.download("stopwords")
nltk.download("punkt")
nltk.download("wordnet")

class NLP_PREPROCESSING:
    STOPWORD = set(stopwords.words('english'))
    PORTER_STEMMER = PorterStemmer()
    LEMMATIZER = WordNetLemmatizer()
    COLORS = ['Pastel1', 'Paired']
    PUNCTUATIONS = string.punctuation
    def __init__(self):
        for p in self.PUNCTUATIONS:
            self.STOPWORD.add(p)

    def do_tokenize(self, sentence):
        return word_tokenize(sentence)

    def do_stopword(self, tokenized_words):
        return [w for w in tokenized_words if not w in self.STOPWORD]
    
    def do_stemming(self, filterd_words):
        return [self.PORTER_STEMMER.stem(fw) for fw in filterd_words]
    
    def do_lemmentize(self, stem_words):
        return [self.LEMMATIZER.lemmatize(sw) for sw in stem_words]
    
    def do_final_data(self, lemmentized_words):
        return " ".join([i for i in lemmentized_words])
    
    def do_plot(self, data):
        for items in range(len(data)):
            plt.figure(figsize=(20, 10))
            pd.Series(" ".join([i for i in data[items]]).split()).value_counts().head(30).plot(kind='bar', colormap = self.COLORS[items])
            plt.show()
            
    def get_lables(self, classes):
        if classes == 1:
            return 'POSITIVE'
        if classes == 0:
            return 'NEGATIVE'
    
    def do_vector_transform(self):
        return TfidfVectorizer(use_idf = True,lowercase = True, strip_accents='ascii',stop_words=self.STOPWORD)

nlp_preprocessing = NLP_PREPROCESSING()

"""### **EDA**"""

df = pd.read_csv('dataset/reviews.txt',sep = '\t', names =['Reviews','Comments'])
df.head()

df['tokenized_comments'] = df['Comments'].apply(lambda x:nlp_preprocessing.do_tokenize(x.lower()))

df.head()

df['filtered_comments'] = df['tokenized_comments'].apply(lambda x:nlp_preprocessing.do_stopword(x))

df.head()

df['stemed_comments'] = df['filtered_comments'].apply(lambda x: nlp_preprocessing.do_stemming(x))

df.head()

df['lemmetized_comments'] = df['stemed_comments'].apply(lambda x: nlp_preprocessing.do_lemmentize(x))

df.head()

df['final_comments'] = df['lemmetized_comments'].apply(lambda x: nlp_preprocessing.do_final_data(x))

df.head()

df['labels'] = df['Reviews'].apply(lambda x: nlp_preprocessing.get_lables(x))

df.head()

positive_review = df[df.labels == "POSITIVE"]['final_comments']
negative_review = df[df.labels == "NEGATIVE"]['final_comments']

data = [positive_review, negative_review]
nlp_preprocessing.do_plot(data)



"""### **MODEL BUILDING**"""

df.head()

tfv = nlp_preprocessing.do_vector_transform()
tfv

X = tfv.fit_transform(df['Comments']).toarray()
y = df['Reviews'].values
joblib.dump(tfv, 'models/transform_vector')
#pickle.dump(tfv, open('tranform.pkl', 'wb'))

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 0)

print(X_train.shape)
print(X_test.shape)
print(y_train.shape)
print(y_test.shape)

"""### **Naive Bayes (GaussianNB)**"""

GaussianNB_classifier = GaussianNB()
GaussianNB_classifier.fit(X_train, y_train)
print(f"TEST SCORE: {GaussianNB_classifier.score(X_test, y_test) * 100}, TRAIN SCORE:{GaussianNB_classifier.score(X_train, y_train) * 100}\n")
GaussianNB_classifier_pred = GaussianNB_classifier.predict(X_test)
print('ACCURACY SCORE: ',accuracy_score(y_test, GaussianNB_classifier_pred) * 100, "\n")
print(f"CONFUSION MATRIX: \n{confusion_matrix(y_test, GaussianNB_classifier_pred)}")

"""### **Naive Bayes(MultinomialNB)**"""

MultinomialNB_classifier = MultinomialNB()
MultinomialNB_classifier.fit(X_train, y_train)
print(f"TEST SCORE: {MultinomialNB_classifier.score(X_test, y_test) * 100}, TRAIN SCORE:{MultinomialNB_classifier.score(X_train, y_train) * 100}\n")
MultinomialNB_classifier_pred = MultinomialNB_classifier.predict(X_test)
print('ACCURACY SCORE: ',accuracy_score(y_test, MultinomialNB_classifier_pred) * 100, "\n")
print(f"CONFUSION MATRIX: \n{confusion_matrix(y_test, MultinomialNB_classifier_pred)}")

"""### **Tree (DecisionTreeClassifier)**"""

DecisionTreeClassifier_classifier = DecisionTreeClassifier(criterion = 'entropy', random_state = 0)
DecisionTreeClassifier_classifier.fit(X_train, y_train)
print(f"TEST SCORE: {DecisionTreeClassifier_classifier.score(X_test, y_test) * 100}, TRAIN SCORE:{DecisionTreeClassifier_classifier.score(X_train, y_train) * 100}\n")
DecisionTreeClassifier_pred = DecisionTreeClassifier_classifier.predict(X_test)
print('ACCURACY SCORE: ',accuracy_score(y_test, DecisionTreeClassifier_pred) * 100, "\n")
print(f"CONFUSION MATRIX: \n{confusion_matrix(y_test, DecisionTreeClassifier_pred)}")

"""### **Ensemble (RandomForestClassifier)**"""

RandomForestClassifier_classifier = RandomForestClassifier(n_estimators = 300, criterion = 'entropy', random_state = 0)
RandomForestClassifier_classifier.fit(X_train, y_train)
print(f"TEST SCORE: {RandomForestClassifier_classifier.score(X_test, y_test) * 100}, TRAIN SCORE:{RandomForestClassifier_classifier.score(X_train, y_train) * 100}\n")
RandomForestClassifier_classifier_pred = RandomForestClassifier_classifier.predict(X_test)
print('ACCURACY SCORE: ',accuracy_score(y_test, RandomForestClassifier_classifier_pred) * 100, "\n")
print(f"CONFUSION MATRIX: \n{confusion_matrix(y_test, RandomForestClassifier_classifier_pred)}")

"""### **Dumping Model**"""

filename = 'models/randomforest_review'
joblib.dump(RandomForestClassifier_classifier, filename)
#pickle.dump(RandomForestClassifier_classifier, open(filename, 'wb'))

movie_review_list = np.array(["this movie was is not amazing."])
transform = tfv.transform(movie_review_list)
pred = MultinomialNB_classifier.predict(transform)
if pred[0] == 0:
    print("Bad")
if pred[0] == 1:
    print("Good")

