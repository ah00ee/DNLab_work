import sqlite3


def address_list(database):
    con = sqlite3.connect(database)
    cur = con.cursor()
    
    # 새로 저장한 주소 + 기존 접속 가능 주소
    cur.execute('select addr from AddrHash_ID where id in (select id from Addr_Valid where availability is NULL or julianday(CURRENT_DATE) - julianday(Date) >= availability)')
    addr_check = cur.fetchall()
    addr_check = [addr[0] for addr in addr_check]

    total, new = cur.execute('select * from AddrHash_ID').fetchall(), cur.execute('select * from Addr_Valid where Date is null').fetchall()
    total, new = len(total), len(new)
       
    con.close()

    return addr_check, total, new


def refresh_availability(database):
    con = sqlite3.connect(database)
    cur = con.cursor()

    # fibonacci 활용
    # availability가 377이 될 경우 더 이상 진행 X
    fibo = [0, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377]
    
    # 접속 가능 주소 가용성 업데이트
    cur.execute('update Addr_Valid set availability = 0 where id in (select id from AddrHash_ID where hash is not null)')

    # 검사 후 접속 불가능 주소 리스트
    cur.execute('select id from AddrHash_ID where id in (select id from Addr_Valid where availability is NULL or julianday(CURRENT_DATE) - julianday(Date) >= availability) and hash is null')
    addr_fail = cur.fetchall()

    # 검사 날짜 업데이트
    cur.execute('update Addr_Valid set Date = CURRENT_DATE where id in (select id from Addr_Valid where availability is NULL or julianday(CURRENT_DATE) - julianday(Date) >= availability)')

    # 접속 불가능 주소 가용성 업데이트
    for id in addr_fail:
        availability = cur.execute('select availability from Addr_Valid where id = "%d"' %id[0]).fetchone()
        
        if availability[0] is None:
            n = 1
        else:
            n = fibo.index(availability[0]) + 1
        cur.execute('update Addr_Valid set availability = "%d" where id = "%d"' %(fibo[n], id[0]))

    con.commit()
    con.close()
