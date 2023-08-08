from typing import Text
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer, PatternAnalyzer
import re
import string
from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


text = "JUST IN - Iran's #bitcoin mining ban will be reversed on Sept 22. Your move, China"

print("raw text: " + text)

text = text.lower()
text = re.sub('\[.*?\]', '', text)
text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
text = re.sub('\w*\d\w*', '', text)
text = re.sub('[‘’“”…]', '', text)
text = re.sub('\n', '', text)

print("cleaned text: " + text)

text_tokens = word_tokenize(text)
clean_tokens = [word for word in text_tokens if not word in stopwords.words()]

final = ""

for token in clean_tokens:
    final += token + " "

print(final)

res = TextBlob(final, analyzer=PatternAnalyzer())
print("polarity: " + str(res.polarity))
print("subjectivity: " + str(res.subjectivity))