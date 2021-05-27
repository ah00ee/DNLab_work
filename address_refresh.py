import multiprocessing
import shutil
import os
import time

from date_update import address_list, refresh_availability
from category_maker import get_category
from html_file_maker import get_address, file_maker, hash_maker, get_args


FLAGS = None
_ = None


def main():
    
    # output 및 html 폴더 생성
    os.makedirs(FLAGS.output, exist_ok=True)
    path_dir = os.path.join(FLAGS.output, 'html')
    
    try:
        os.makedirs(path_dir, exist_ok=False)    
    except FileExistsError:
        shutil.rmtree(path_dir)
        os.makedirs(path_dir, exist_ok=True)

    addresses, total, new = address_list(FLAGS.input)

    get_args(FLAGS)
    
    # html 파일 생성
    print(f'Start html file making')
    with multiprocessing.Pool(FLAGS.number) as p:
        joined_rows = p.imap(file_maker, get_address(addresses))
        
        for row in joined_rows:
            print(row)
    
    # hash 생성 및 업데이트
    print("Start updating hash...")
    hash_maker(FLAGS.input, path_dir)
    
    # 수집일 갱신
    print("Start updating date...")
    available = refresh_availability(FLAGS.input)

    # 카테고리 생성
    print("Start updating category...")
    get_category(FLAGS.input, path_dir)

    print("\nFinish testing onion address\n>>>Total: '%d' | # of new address: '%d' | # of available address: '%d'"%(total, new, available))
    
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    
    parser.add_argument('-i', '--input', type=str, required='True',
                        help='The addresses formed database for testing')
    parser.add_argument('-o', '--output', type=str,
                        default='/home/ahyoung/Desktop/tor-folder/final/output',
                        help='The output directory for saving html files')
    parser.add_argument('-p', '--port', type=int,
                        default=9050,
                        help='The port number of Tor socks5h server')
    parser.add_argument('-n', '--number', type=int,
                        default=multiprocessing.cpu_count()*2,
                        help='The number of process pool')
    FLAGS, _ = parser.parse_known_args()
    
    # path preprocessing
    FLAGS.input = os.path.abspath(os.path.expanduser(FLAGS.input))
    FLAGS.output = os.path.abspath(os.path.expanduser(FLAGS.output))

    main()
