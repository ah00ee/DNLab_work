import sqlite3
import pickle
from nltk.corpus import stopwords
from nltk import WordNetLemmatizer, word_tokenize
import os
import re


def dictionary(dpath):
    with open(dpath, 'rb') as f:
        return pickle.load(f)
    

def crawl_data(data):
    lmt = WordNetLemmatizer()
    sw = stopwords.words('english')
    sw = sw + ['tr', 'td', 'thead', 'th', 'tbody', 'li', 'tfoot', 'child', 'nbsp']

    #html tag, css 부분 제거 + '\n', '\r', '\t'제거
    html = re.sub(pattern='<([^>]+)>|{[^>]*}|[-=+,!?"\(|\)"]|\n\t|\t\n|\n|\t|\r', repl='', string=data)
    tokens = word_tokenize(html)
    words = set()

    for token in tokens:
        word = token.lower()
        if word not in sw and word.isalpha():
            words.add(lmt.lemmatize(word))

    return words


def find_features(doc, word_features):
    words = set(doc)
    features = {}
    
    for w in word_features:
        features[w] = (w in words)

    return features


def get_category(database, path_dir):
    file_list = os.listdir(path_dir)

    con = sqlite3.connect(database)
    cur = con.cursor()

    d = dictionary('category_words.txt')
    for f in file_list:    
        fpath = os.path.join(path_dir, f)
        print(f)
        data, maximum, category = '', 0.1, 'etc.'
        
        for key in d.keys():
            print(key, end=': ')
            word_features, cnt = d[key], 0

            with open(fpath, 'r') as f:
                data = f.read()
                features = find_features(crawl_data(data), word_features)
                for value in features.values():
                    if value:
                        cnt += 1
                cnt = ((cnt/len(features))*100)
                if cnt > maximum:
                    maximum = cnt
                    category = key
            print(cnt)

        c = cur.execute('select id from CategoryID where category = "%s"'%(category)).fetchone()[0]
        cur.execute('update AddrCategory set category = "%d" where addr = "%d"'%(c, f[:-5]))
        print()

    con.commit()
    con.close()