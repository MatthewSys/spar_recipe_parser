import psycopg2
from bs4 import BeautifulSoup as Bs
from imap_tools import MailBox, AND

import conf


def main():
    mb = MailBox(conf.server).login(conf.username, conf.password)
    messages = mb.fetch(criteria=AND(from_=conf.inbound), mark_seen=False)
    for msg in messages:
        processing(msg)


def processing(msg):
    conf.lst.clear()
    soup = Bs(msg.html, 'lxml')
    span = soup.find_all('span')
    for i in span:
        st_r = i.text
        st_r.strip()
        conf.lst.append(st_r)
    stripped = [s.strip() for s in conf.lst]
    len_s = len(stripped)
    if stripped[1] == conf.detect:
        name = stripped[14:len_s:8]
        qua = stripped[15:len_s:8]
        cost = stripped[16:len_s:8]
    else:
        name = stripped[14:len_s:10]
        qua = stripped[15:len_s:10]
        cost = stripped[16:len_s:10]
    del cost[-2:]
    del name[-3:]
    del qua[-3:]
    if cost[-1] == conf.defect:
        del cost[-1:]
    date = stripped[4]
    convertor(name, qua, cost, date)


def convertor(name, qua, cost, date):
    conf.summ.clear()
    qua = [float(f) for f in qua]
    cost = [float(c) for c in cost]
    for i, j in zip(cost, qua):
        s = i * j
        smoked = float("{:.2f}".format(s))
        conf.summ.append(smoked)
    smrz = conf.summ
    todb(name, cost, qua, smrz, date)


def todb(name, cost, qua, smrz, date):
    con = psycopg2.connect(database=conf.dbname, user=conf.dbuser, password=conf.dbpass, host=conf.dbhost,
                           port=conf.dbport)
    cur = con.cursor()
    for n, c, q, s in zip(name, cost, qua, smrz):
        cur.execute(
            "INSERT INTO spar (name,cost,qua,sum,time) VALUES (%s,%s,%s,%s,%s)", (n, c, q, s, date))
    con.commit()
    con.close()


if __name__ == '__main__':
    main()
