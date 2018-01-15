import csv
import socket
import urllib2
import json
import os
import logging
from functools import partial
from multiprocessing.pool import Pool
from contextlib import closing
from datetime import datetime

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO, filename='update_check.log')
LOG = logging.getLogger(__name__)
cwd = os.getcwd()


def change_error_result_file(cluster_ip_list, fp, text):
    error_file = cluster_ip_list + "/cluster_ip_list/" + fp
    LOG.debug(text + " append to " + error_file)
    with open(error_file, "a") as f:
        f.write(text + "\n")
    return True


tenant_map = {"rheosBehaviorStaging": "dev", "dev": "dev", "prod": "mpt-prod", "sherlock-Streams": "mpt-prod"}


def get_tenant(key_tenant):
    with open('tenant', 'rb') as fp_ten:
        tenant_dict = dict()
        for item in fp_ten:
            if ":" in item:
                key, value = item.split(":", 1)
                tenant_dict[key] = value
    return tenant_dict[key_tenant]


def get_status_code(az, tenant, node_id):
    uri = 'http://os-straas.vip.' + az + '.ebayc3.com:9090/straas/v1.0/nodes/' + node_id + '/commands'
    LOG.debug(uri + " call api")
    body_value = {"command": "list-commands", "args": ""}
    request = urllib2.Request(uri, data=json.dumps(body_value))
    request.add_header('Content-Type', 'application/json')
    request.add_header('user', 'a')
    request.add_header('tenant', tenant)
    request.add_header('token', 'a')
    request.add_header('Accept', 'application/json')
    try:
        response = urllib2.urlopen(request, timeout=20).read()
        data = json.loads(response)
        status_code = data['status_code']
        LOG.info(status_code)
    except urllib2.URLError, e:
        status_code = 'not pingable'
        LOG.info(status_code + ':' + e)
    except socket.timeout as se:
        status_code = 'not pingable'
        LOG.info(status_code + ':' + se)
    return status_code


def multipro(az, tenant, id_dic):
    error_code = get_status_code(az, tenant, id_dic["node_id"])
    l = []
    if error_code != 200:
        l.append(id_dic["fqdn"])
        l.append(id_dic["node_id"])
        l.append(error_code)
        print id_dic
    return l


def check_solve_status(az, tenant, cluster_ip_list, check_result_list):
    dic = {}
    LOG.info("start crawl error_node .....")
    with open(cluster_ip_list + "/cluster_ip_list/" + "all_fqdn_id_list", 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        id_dic_list = [row for row in reader]
        check_status = partial(multipro, az, tenant)
        pool = Pool(20)
        with closing(pool) as p:
            result_list = p.map(check_status, id_dic_list)
            p.terminate()
        print result_list
        for result in result_list:
            if result.__len__() != 0:
                change_error_result_file(cluster_ip_list, "error_fqdn_list", result[0])
                change_error_result_file(check_result_list, "error_fqdn_list_" +
                                         (datetime.today().weekday() + 1).__str__(), result[0])
                change_error_result_file(cluster_ip_list, "error_fqdn_status_list",
                                         result[0] + ' ' + result[1] + ' error_code ' + result[2])


if __name__ == '__main__':
    az_list = ["lvs01", "lvs02", "slc01", "slc07", "phx01", "phx02"]
    vpc_list = ["dev", "rheosBehaviorStaging"]

    for vpc_name in vpc_list:
        for az_name in az_list:
            line_ten = get_tenant(str(vpc_name).strip())
            cluster_ip_list = cwd + "/" + vpc_name + "_" + az_name
            check_result_list = cwd + "/" + "check_result_list" + "/" + vpc_name + "_" + az_name
            if not os.path.exists(check_result_list + "/cluster_ip_list/"):
                os.makedirs(check_result_list)
                os.makedirs(check_result_list + "/cluster_ip_list/")
            today_err_list = check_result_list + "/cluster_ip_list/" + "error_fqdn_list_" + (datetime.today().weekday() + 1).__str__()
            if os.path.exists(today_err_list):
                os.remove(today_err_list)
            check_solve_status(az_name, str(line_ten).strip(), cluster_ip_list, check_result_list)
