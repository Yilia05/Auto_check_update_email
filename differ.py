from datetime import datetime


def differ():
    s1 = set(open('test1', 'r').readlines())
    s2 = set(open('test2', 'r').readlines())
    print 'dif: %s' % (s1.difference(s2))
    ss = s1.difference(s2)
    with open('resultttt', 'wb') as re:
        re.writelines(ss)


if __name__ == '__main__':
    print (datetime.today().weekday()+1).__str__()+" week"
    # print datetime.today().isocalendar().index(2)
    # print datetime.today().isocalendar().index(2).__str__()+'week'
    # differ()