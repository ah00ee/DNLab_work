import requests
import sqlite3
import hashlib
import os
import time

global FLAGS
FLAGS = None


def get_args(args):
    global FLAGS
    FLAGS = args


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
            addr = 'http://' + row + '.onion'
            data = session.get(addr).text
            #time.sleep(2)
        except requests.exceptions.ConnectionError:
            return {'Address': row, 'Result': 'Fail'}

        if '/' in row:
            return {'Address': row, 'Result': 'Fail'}

        fpath = os.path.join(FLAGS.output, 'html', f'{row}.html')
        
        with open(fpath, 'w') as f:
            f.write(data)

    return {'Address': row, 'Result': 'Success'}


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

    # hash 상태 초기화
    cur.execute('update AddrHash_ID set hash = null')
    
    for f in file_list:
        fpath = os.path.join(path_dir, f)
        hash = encrypt_file(fpath)
        cur.execute('UPDATE AddrHash_ID SET hash = "%s" WHERE addr = "%s"'%(hash, f[:-5]))
    
    con.commit()
    con.close()
