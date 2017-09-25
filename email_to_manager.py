#!/usr/bin/env python
# coding: utf-8
from email.header import Header
from email.mime.text import MIMEText
from smtplib import SMTP
from poplib import POP3
from time import sleep
import os
import util
from crawl_all import LOG

update_result_path = os.getcwd() + "/" + 'update_result_list/'


def sendmail(az_name, vpc_name):
    SMTPServer = 'atom.corp.ebay.com'
    POPServer = 'pop.corp.ebay.com'
    subject = '[dev] [' + az_name  + '] [' + vpc_name + '] [WRONG_NODE]'
    Heads1 = ['From: yzhang46@ebay.com', 'To: lubliu@ebay.com', 'Subject: %s' % subject]
    LOG.info(Heads1)
    Body1 = get_body(az_name)
    Body2 = get_body2(az_name, vpc_name)
    send_sev = SMTP(SMTPServer)
    LOG.info('sending emails to managers')
    Body = util.to_html(Body1 + Body2)

    if Body1 or Body2:
        sendmsg = MIMEText(Body, _subtype='html',_charset='gb2312')
        sendmsg['Subject'] = Header(subject, 'utf-8')
        sendmsg['From'] = 'Straas_Check_Alert'
        sendmsg['To'] = 'yzhang46@ebay.com'
        # sendmsg = '\r\n\r\n'.join(['\r\n'.join(Heads1), msg.as_string()])
        try:
            send_sev.sendmail('yzhang46@ebay.com', ('yzhang46@ebay.com', 'yzhang46@ebay.com'), sendmsg.as_string())
        except Exception as e:
            LOG.info('send failed')
    else:
        LOG.info('No email need to send')
    try:
        send_sev.quit()
        LOG.info('email success')
    except Exception as e:
        LOG.info('email failed')
        LOG.info(e)


def differ(fp1, fp2):
    if os.path.exists(fp1) and os.path.exists(fp2):
        s1 = set(open(fp1, 'r').readlines())
        s2 = set(open(fp2, 'r').readlines())
        ss = s1.difference(s2).union(s2.difference(s1))
        with open('differ_result', 'wb') as re:
            re.writelines(ss)
    else:
        return ''


def get_body2(az_name, vpc_name):
    fp1 = update_result_path + az_name + '/' + 'all_err_node'
    if az_name.find('_'):
        az_name = az_name[-5:]
    list_path = os.getcwd() + "/" + vpc_name + "_" + az_name + "/cluster_ip_list/" + "error_fqdn_list"
    differ(fp1, list_path)
    if os.path.exists('differ_result'):
        with open('differ_result', 'r') as fs:
            context = fs.read()
            if context.strip() == '':
                LOG.info('no differ' + context)
                return ""
            else:
                LOG.info('fs.read:' + context + 'over')
                unknow_reason_body = 'unknow reason list : \r\n' + context + '\r\n'
                return unknow_reason_body
    else:
        return ""


def get_body(az_name):
    filepath = update_result_path + az_name + '/'
    # filepath = 'testall/'
    all_dir_body = ''
    path_dir = os.listdir(filepath)
    LOG.info(path_dir)
    for all_dir in path_dir:
        with open(filepath + all_dir, 'r') as fa:
            all_dir_body += '%s\r\n\r\n' % (all_dir + '\r\n' + fa.read())
    return all_dir_body


if __name__ == "__main__":
    az_list = ['lvs01', 'lvs02', 'slc01', 'slc07', 'phx01', 'phx02']
    staging_az_list = ['staging_lvs01', 'staging_lvs02', 'staging_phx01', 'staging_phx02', 'staging_slc01', 'staging_slc07']

    for dev_az in az_list:
        sendmail(dev_az, 'dev')
    for staging_az in staging_az_list:
        sendmail(staging_az, 'rheosBehaviorStaging')