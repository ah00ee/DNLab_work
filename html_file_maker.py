import requests
import sqlite3
import hashlib
import os


FLAGS = None


def get_args(args):
    global FLAGS
    FLAGS = args
    print(FLAGS.port)
    

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


    # output 및 html 폴더 생성
    os.makedirs(FLAGS.output, exist_ok=True)
    path_dir = os.path.join(FLAGS.output, 'html')

    try:
        os.makedirs(path_dir, exist_ok=False)    
    except FileExistsError:
        shutil.rmtree(path_dir)
        os.makedirs(path_dir, exist_ok=True)

    addresses = address_list(FLAGS.input)

    # html 파일 생성
    print(f'Start html file making')

    time_start = time.time()
    with multiprocessing.Pool(FLAGS.number) as p:
        joined_rows = p.imap(file_maker, get_address(addresses))
        for row in joined_rows:
            print(row)
    time_end = time.time()


def file_maker(row):  
    session = get_session()
    if type(row) is not list:
        try:
            addr = 'http://' + row + '.onion'
            data = session.get(addr).text
        except requests.exceptions.ConnectionError:
            return {'Address': row, 'Result': 'Fail'}

        if '/' in row:
            return {'Address': row, 'Result': 'Fail'}

        fpath = os.path.join(FLAGS.output, 'html', f'{row}.html')
        print(fpath, end=" ")
        
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
    file_list = os.listdir(database)

    con = sqlite3.connect(FLAGS.input)
    cur = con.cursor()
    
    for f in file_list:
        fpath = os.path.join(path_dir, f)
        hash = encrypt_file(fpath)
        cur.execute('UPDATE AddrHash_ID SET hash = "%s" WHERE addr = "%s"'%(hash, f[:-5]))
    
    con.commit()
    con.close()