import sqlite3

def get_hash(database):
    con = sqlite3.connect(database)
    cur = con.cursor()

    # 새로 저장한 주소 + 기존 접속 가능 주소
    cur.execute('select addr from AddrHash_ID where id in (select id from Addr_Valid where availability is NULL or julianday(CURRENT_DATE) - julianday(Date) => availability)')
    addr_valid = cur.fetchall()
    addr_valid = [addr[0] for addr in addr_valid]
    
    con.close()

    return addr_valid


def refresh_availability(database):
    con = sqlite3.connect(database)
    cur = con.cursor()

    # fibonacci 활용
    # availability가 377이 될 경우 더 이상 진행 X
    fibo = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377]

    # 갱신하지 않는 주소
    cur.execute('select id from Addr_Valid where availability < 377 and julianday(CURRENT_DATE) - julianday(Date) < availability')
    addr_invalid = cur.fetchall()

    for id in addr_invalid:
        availability = cur.execute('select availability from Addr_Valid where id = "%d"' %id[0]).fetchone()
        if availability == None:
            cur.execute('update Addr_Valid set availability = 1, Date =  CURRENT_DATE where id = "%d"' %id[0])
        else:
            n = fibo.index(availability[0]) + 1
            cur.execute('update Addr_Valid set availabiliy = "%d", Date = CURRENT_DATE where id = "%d"' %(n, id[0]))
    
    con.commit()
    con.close()