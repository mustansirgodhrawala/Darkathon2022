import os
import pickle

import pandas as pd
from bs4 import BeautifulSoup

data = []
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import GridSearchCV
from sklearn import svm


def clean(text):
    data = " ".join(text.replace("\n", "").strip().lower().split())
    return data


# print("Building df")
# for filename in os.listdir('dataset/drugs'):
# 	f = os.path.join('dataset/drugs', filename)
# 	with open(f,"r") as file:
# 		soup = BeautifulSoup(file.read(),"html5lib")
# 		[s.extract() for s in soup(['style', 'script', '[document]'])]
# 		visible_text = soup.get_text()
# 		data.append([clean(visible_text),"drugs"])

# for filename in os.listdir('dataset/notdrugs'):
# 	f = os.path.join('dataset/notdrugs', filename)
# 	with open(f,"r") as file:
# 		soup = BeautifulSoup(file.read(),"html5lib")
# 		[s.extract() for s in soup(['style', 'script', '[document]', 'head', 'title'])]
# 		visible_text = soup.getText()
# 		data.append([clean(visible_text),"notdrugs"])

# dataframe = pd.DataFrame(data, columns=["Text","Label"])
dataframe = pd.read_csv("dataset.csv")
dataframe = dataframe.drop_duplicates(keep="first")
print("Built df")
X = dataframe["Text"].values.astype("U")
y = dataframe["Label"].values.astype("U")

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=109
)  # 70% training and 30% test

# Import svm model
from sklearn import svm

# Converting String to Integer
cv = CountVectorizer()
X_train = cv.fit_transform(X_train)
X_test = cv.transform(X_test)

# Converting String to Integer
from sklearn.svm import SVC
from sklearn import metrics

print("Building SVM Model")
classifier = SVC(kernel="linear")
classifier.fit(X_train, y_train)
y_pred = classifier.predict(cv.transform(["sadasdasdas"]))
print(y_pred)
