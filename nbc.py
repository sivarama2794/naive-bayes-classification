"""
Naive bayes classification implementation in python
"""
import os
import pandas as pandas
import ijson
from nltk.stem.porter import PorterStemmer
from collections import defaultdict

TEST_FOLDER_PATH = "/Users/vasanthmahendran/Workspace/Data/nbc/test"
TRAIN_FOLDER_PATH = "/Users/vasanthmahendran/Workspace/Data/nbc/train"
COLUMN_NAMES = ['Ratings', 'AuthorLocation', 'Title', 'Author', 'ReviewID', 'Content', 'Date']
STEMMER = PorterStemmer()
class NaiveBayesClassification(object):
    def __init__(self):
        self.pd_datas_train = self.parsefiles(TRAIN_FOLDER_PATH)
        self.pd_datas_test = self.parsefiles(TEST_FOLDER_PATH)
        self.pd_datas_train['class'] = self.pd_datas_train['Ratings'].map(lambda x: 'positive' if float(x) > 3 else 'negative')
        self.pd_datas_train['Content'] = self.pd_datas_train['Content'].map(lambda x: self.pre_processing(x))
        self.pd_datas_test['class'] = self.pd_datas_test['Ratings'].map(lambda x: 'positive' if float(x) > 3 else 'negative')
        self.pd_datas_test['Content'] = self.pd_datas_test['Content'].map(lambda x: self.pre_processing(x))
        self.frequency = defaultdict(int)
        self.frequency_positive = defaultdict(int)
        self.frequency_negative = defaultdict(int)
        self.frequency_total = len(self.pd_datas_train.index)
        self.pd_datas_train['Content'].apply(lambda x: self.build_frequency(x))
        self.bin = len(self.frequency)
        pd_datas_train_positives= self.pd_datas_train.loc[self.pd_datas_train['class'] == 'positive']
        pd_datas_train_negatives= self.pd_datas_train.loc[self.pd_datas_train['class'] == 'negative']
        self.positive_probability_freq = len(pd_datas_train_positives.index)
        self.negative_probability_freq = len(pd_datas_train_negatives.index)
        pd_datas_train_positives['Content'].apply(lambda x: self.build_frequency_positive(x))
        pd_datas_train_negatives['Content'].apply(lambda x: self.build_frequency_negative(x))
        self.pd_datas_test = self.pd_datas_test.merge(self.pd_datas_test.apply(self.process, axis=1), left_index=True, right_index=True)
        accuracy = self.calculate_accuracy(self.pd_datas_test['class'], self.pd_datas_test['predicted_class'])
        print('accuracy-----',accuracy)
        pandas.DataFrame(self.pd_datas_test).to_csv('result.csv', index=False)

    def parsefiles(self,folder_path):
        pd_datas = pandas.DataFrame([], columns=COLUMN_NAMES)
        for file in os.listdir(folder_path):
            data = []
            if file.endswith(".json"):
                file_path = os.path.join(folder_path, file)
                if os.path.isfile(file_path):
                    with open(file_path, 'r') as file:
                        objects = ijson.items(file, 'Reviews.item')
                        for row in objects:
                            selected_row = []
                            for item in COLUMN_NAMES:
                                if item == 'Ratings':
                                    selected_row.append(row[item]['Overall'])
                                else:
                                    selected_row.append(row[item])
                            data.append(selected_row)
                        pd_datas = pd_datas.append(pandas.DataFrame(data, columns=COLUMN_NAMES))
        return pd_datas
    
    def pre_processing(self, s):
        try:
            if isinstance(s, str):
                s = s.lower()
                escape_letters = ["$","  ","?",",","//","..","."," . "," / ","-"," \\"]
                for escape_letter in escape_letters:
                    s = s.replace(escape_letter," ")
                s = (" ").join([STEMMER.stem(z) for z in s.split(" ")])
                return s
            else:
                return " "
        except Exception as error:
            print("str causing error",s,repr(error))
            return " "
    
    def process(self,x):
        words = x['Content'].split(" ")
        positive_prob_product = 1
        negative_prob_product = 1
        for word in words:
            if word:
                positive_prob = (self.frequency_positive[word] + 1)/(self.bin+self.frequency_positive_total)
                negative_prob = (self.frequency_negative[word] + 1)/(self.bin+self.frequency_negative_total)
                positive_prob_product = positive_prob_product * positive_prob
                negative_prob_product = negative_prob_product * negative_prob
        
        positive_prob_product = positive_prob_product * (self.positive_probability_freq/self.frequency_total)
        negative_prob_product = negative_prob_product * (self.negative_probability_freq/self.frequency_total)

        if positive_prob_product > negative_prob_product :
            return pandas.Series(dict(predicted_class="positive"))
        else:
            return pandas.Series(dict(predicted_class="negative"))
    
    def build_frequency(self,x):
        title_row = []
        title_set = x.split(" ")
        for word in title_set:
            if word:
                if word not in title_row:
                    title_row.append(word)
                    self.frequency[word] += 1

    def build_frequency_positive(self,x):
        title_row = []
        title_set = x.split(" ")
        for word in title_set:
            if word:
                self.frequency_positive_total = +1
                if word not in title_row:
                    title_row.append(word)
                    self.frequency_positive[word] += 1
    
    def build_frequency_negative(self,x):
        title_row = []
        title_set = x.split(" ")
        for word in title_set:
            if word:
                self.frequency_negative_total = +1
                if word not in title_row:
                    title_row.append(word)
                    self.frequency_negative[word] += 1
    
    def calculate_accuracy(self,labeled_class, predicted_class):
        correct = 0
        for idx, row in labeled_class.iteritems():
            if row == predicted_class[idx]:
                correct += 1
        return correct / len(labeled_class)
            
            
NBC = NaiveBayesClassification()
