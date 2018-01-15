import os

from update import LOG
from util import blocks
whitelist = os.getcwd() + "/" + 'whitelist'


def ignore_old_wrong_node(str, fp2):
    if os.path.exists(fp2):
        s2 = set(open('test2', 'r').readlines())
        print s2
        print str
        if str in s2:
            LOG.info('true')
            return ''
        else:
            LOG.info('false')
            return str


def generate_new_wrong_list(context, fp2):
    prebody = ''
    graylist = ''
    for block in blocks(context):
        if len(block):
            head = (block[0]+'\r\n')
            graylist += (block[0]+'\r\n')
            # prebody += (block[0]+'\r\n')
            for i in range(1, block.__len__()):
                precontent = ''
                string = str(block[i]).strip()+'\n'
                newstr = ignore_old_wrong_node(string, fp2)
                if newstr == '':
                    graylist += string
                precontent += newstr
            if precontent == '':
                prebody += precontent
            else:
                prebody += head
                prebody += precontent
            prebody += '\r\n\r\n'
            graylist += '\r\n\r\n'
    return prebody, graylist


def count_err_time(az_name, vpc_name):
    dic = {}
    for num in range(1, 7):
        check_result_list = os.getcwd() + "/" + "check_result_list" + "/" + vpc_name + "_" + az_name
        list_path = check_result_list + "/cluster_ip_list/" + "error_fqdn_list_" + num.__str__()
        if os.path.exists(list_path):
            with open(list_path, 'rb') as fpr:
                lines = fpr.readlines()
                for line in lines:
                    line = line.strip()
                    if dic.get(line) is None:
                        dic[line] = 1
                    elif dic.get(line) is not None:
                        dic[line] += 1
    for i in dic:
        if dic[i] > 2:
            with open(whitelist, 'a') as wl:
                wl.write(i + "\n")


def handle_pre_body(prebodys):
    prebodyset = set(prebodys.split())
    print prebodyset
    titleset = {'all_err_node:',
                'f_err_base:',
                'f_err_disk_full:',
                'f_err_network:',
                'f_err_too_old_node:',
                'unknow reason list:',
                'update_file_success:'}
    handle_res = prebodyset.difference(titleset)
    print handle_res
    return handle_res

if __name__ == '__main__':
    with open('test1', 'rb') as res:
        result = res.read()
    #print generate_new_wrong_list(result, 'test2').__len__()
    new_wrong_list = generate_new_wrong_list(result, 'test2')[0]
    handled_body = handle_pre_body(new_wrong_list)
    blacklist = generate_new_wrong_list(result, 'test2')[1]
    with open('blacklist', 'wb') as bl:
        bl.write(blacklist)
    if handled_body.__len__() is 0:
        with open('resulttt', 'wb') as w:
            w.write('')
            print 'no email need to send '
    else:
        with open('resulttt', 'wb') as w:
            w.write(new_wrong_list)

