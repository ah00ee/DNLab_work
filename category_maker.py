import sqlite3
import pickle
from nltk.corpus import stopwords
from nltk import WordNetLemmatizer, word_tokenize
import os
import re
from collections import Counter, defaultdict

lmt = WordNetLemmatizer()
sw = stopwords.words('english')
sw = sw + ['tr', 'td', 'thead', 'th', 'tbody', 'li', 'tfoot', 'child', 'nbsp']

addr = cur.execute('select id, addr from ah where hash is not null').fetchall()


def dictionary(dpath):
    with open(dpath, 'rb') as f:
        return pickle.load(f)
    

def count_words(data):
    total = Counter()

    fname = data + '.html'
    fpath = os.path.join(path_dir, fname)
    
    with open(fpath, 'r') as f:
        data = crawl_data(f.read())
        vocab = Counter(data)
        total += vocab
    total = dict(total.most_common(30))
    
    return total
    

def crawl_data(data):
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
    con = sqlite3.connect(database)
    cur = con.cursor()

    d = dictionary('category_words.txt')
    for file in addr:    
        fpath = os.path.join(path_dir, file[1] + ".html")
        print(file)
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
        cur.execute('update ac set category = "%d" where addr = "%d"'%(c, file[0]))
        print()
    con.commit()
    con.close()