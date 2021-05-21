import time
import requests
import sqlite3
import hashlib
import os


def get_address(rows):
    for row in rows:
        yield row


def get_session(): 
    session = requests.session()
    session.proxies = {}
    session.proxies['http'] = f'socks5h://localhost:{FLAGS.port}'
    session.proxies['https'] = f'socks5h://localhost:{FLAGS.port}'
    session.headers['User-Agent'] = 'Mozilla/5.0'
    return session


def file_maker(row):    
    session = get_session()
    if type(row) is not list:

        try:
            addr = 'http://' + row[0] + '.onion'
            data = session.get(addr).text

        except requests.exceptions.ConnectionError:
            return {'Address': row[0], 'Result': 'Fail'}

        if '/' in row[0]:
            return {'Address': row[0], 'Result': 'Fail'}

        path_html = os.path.join(FLAGS.output, 'html', f'{row[0]}.html')
        print(path_html, end=" ")
        
        with open(path_html, 'w') as f:
            f.write(data)
    return {'Address': row[0], 'Result': 'Success'}


def encrypt_file(html, blocksize=65536):
    f = open(html, 'rb')
    hasher = hashlib.sha256()

    while True:
        buf = f.read(blocksize)
        if not buf:
            break
        hasher.update(buf)
    f.close()
    return hasher.hexdigest()


def hash_maker(database, path_dir):
    file_list = os.listdir(path_dir)

    con = sqlite3.connect(database)
    cur = con.cursor()

    for f in file_list:
        path = os.path.join(path_dir, f)
        hash = encrypt_file(path)
        cur.execute('UPDATE AddrHash_ID SET hash = "%s" WHERE addr = "%s"'%(hash, f[:-5]))
    
    con.commit()
    con.close()