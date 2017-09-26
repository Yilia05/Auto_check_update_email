def differ():
    s1 = set(open('test1', 'r').readlines())
    s2 = set(open('test2', 'r').readlines())
    print 'dif: %s' % (s1.difference(s2).union(s2.difference(s1)))
    ss = s1.difference(s2).union(s2.difference(s1))
    with open('resultttt','wb') as re:
        re.writelines(ss)


if __name__ == '__main__':
    differ()