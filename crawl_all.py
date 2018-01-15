import urllib2
import json
import sys
import os
import collections
import logging
import shutil
import csv
from datetime import time
from socket import error as SocketError
import errno

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO, filename='update_check.log')
LOG = logging.getLogger(__name__)
cwd = os.getcwd()


def isNullOrEmpty(stri):
    if not stri or stri.isspace():
        return True
    else:
        return False


def operDir(dirPath, mode='c'):
    if isNullOrEmpty(dirPath):
        LOG.error('dir path is empty or null')
        sys.exit
    if mode == 'c':
        if not os.path.exists(dirPath):
            os.makedirs(dirPath)
            LOG.debug('dir created: %s' % dirPath)
    if mode == 'd':
        if os.path.exists(dirPath):
            os.remove(dirPath)
            LOG.debug('dir deleted: %s' % dirPath)
    if mode == 'dd':
        if os.path.exists(dirPath):
            shutil.rmtree(dirPath)
            LOG.debug('dir files deleted: %s' % dirPath)


def get_tenant(key_tenant):
    with open('tenant', 'rb') as fp_ten:
        tenant_dict = dict()
        for item in fp_ten:
            if ":" in item:
                key, value = item.split(":", 1)
                tenant_dict[key] = value
    return tenant_dict[key_tenant]


def getNodeData(az, tenant):
    uri = 'http://os-straas.vip.' + az + '.ebayc3.com:9090/straas/v1.0/topologies'
    LOG.debug(uri + " call api")
    request = urllib2.Request(uri)
    request.add_header('Content-Type', 'application/json')
    request.add_header('user', 'a')
    request.add_header('tenant', tenant)
    request.add_header('token', 'a')
    LOG.info(request.headers)
    try:
        response = urllib2.urlopen(request).read()
        data = json.loads(response)
    except SocketError as e:
        LOG.info(az + e.__str__())
        data = ''
    return data


tenant_map = {"rheosBehaviorStaging": "dev", "dev": "dev", "prod": "mpt-prod", "sherlock-Streams": "mpt-prod"}


def sort_dict(cluster_dict):
    return collections.OrderedDict(sorted(cluster_dict.items(), key=lambda d: len(d[1])))


def generate_remain_batch_file(cluster_ip_list, batch_name_file, order_cluster_dic):
    with open(cluster_ip_list + "/cluster_ip_list/" + batch_name_file, 'w') as fp_batch:
        for key, value_list in order_cluster_dic.items():
            for value in value_list:
                fp_batch.write(value + '\n')


def generate_mapping_file(cluster_ip_list, fqdn_id_dict):
    with open(cluster_ip_list + "/cluster_ip_list/" + "all_fqdn_id_list", 'wb') as f:
        headers = ['node_id', 'fqdn']
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(fqdn_id_dict)


def generate_min_batch_file(cluster_ip_list, batch_name_file, order_cluster_dict, n):
    with open(cluster_ip_list + "/cluster_ip_list/" + batch_name_file, 'w') as fp_batch:
        if len(order_cluster_dict) < n:
            n = len(order_cluster_dict)
        while n:
            key = order_cluster_dict.items()[0][0]
            value_list = order_cluster_dict.items()[0][1]
            for ip in value_list:
                fp_batch.write(ip + '\n')
            del order_cluster_dict[key]
            n = n-1
    return key


def writeFile(data, fp, fp1, az_name, vpc_name, cluster_ip_list):
    fqdn_id_list = []
    clusters_dict = dict()
    for i in range(len(data)):
        new_list = []
        cluster = data[i]
        name = cluster['name']
        avaliable_zone = cluster['availability_zone']
        components = cluster['components']
        owner = cluster['owner']
        vpc = cluster['vpc']
        if avaliable_zone != az_name:
            fp1.write('availability_zone: ' + str(avaliable_zone) + '  cluster_name: ' + str(name) + '  owner: ' + str(
                owner) + '  vpc: ' + str(vpc))
            fp1.write('\n')
        else:
            if vpc == str(tenant_map[vpc_name]).strip():
                for j in range(len(components)):
                    component = components[j]
                    nodes = component['nodes']
                    for k in range(len(nodes)):
                        fqdn_dict = {}
                        node = nodes[k]
                        ip = str(node['ip_address']).strip()
                        fqdn = str(node['fqdn']).strip()
                        node_id = node['id']
                        LOG.info(fqdn + " valid fqdn")
                        new_list.append(fqdn)
                        fqdn_dict['node_id'] = node_id
                        fqdn_dict['fqdn'] = fqdn
                        fqdn_id_list.append(fqdn_dict)

        if len(new_list) != 0:
            clusters_dict[name] = new_list
    LOG.info("saving dict.....")
    generate_mapping_file(cluster_ip_list, fqdn_id_list)

    order_cluster_dict = sort_dict(clusters_dict)
    generate_remain_batch_file(cluster_ip_list, "all_cluster_ip_list", order_cluster_dict)


def crawl_nodes(az_name, vpc):
    key_ten = vpc
    cluster_ip_list = cwd + "/" + vpc + "_" + az_name
    operDir(cluster_ip_list, 'dd')
    operDir(cluster_ip_list + "/cluster_ip_list")

    fp1 = open(cluster_ip_list + '/' + 'ip_not_' + str(az_name).strip(), 'w')
    fp = open(cluster_ip_list + '/' + 'not_pingable_ip_' + str(az_name).strip(), 'w')

    LOG.info("start get node data ")
    line_ten = get_tenant(str(key_ten).strip())
    node_data = getNodeData(str(az_name).strip(), str(line_ten).strip())
    LOG.info("write node ip in file ")
    writeFile(node_data, fp, fp1, az_name, vpc, cluster_ip_list)
    fp1.close()
    fp.close()
    LOG.info("task end")


az_list = ["lvs01", "lvs02", "slc01", "slc07", "phx01", "phx02"]
vpc_list = ["dev", "rheosBehaviorStaging", "prod"]


if __name__ == '__main__':
    for vpc_name in vpc_list:
        for az_name in az_list:
            crawl_nodes(az_name, vpc_name)
            time.sleep(0.5)