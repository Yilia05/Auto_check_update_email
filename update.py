import csv
from fabric.api import *
from fabric.operations import *
from fabric.context_managers import *
import time
import os
from fabric.io import OutputLooper
import logging
import shutil
from fabric.contrib.files import exists
from fabric.exceptions import NetworkError
from paramiko.ssh_exception import SSHException
from fabric.exceptions import CommandTimeout


env.user = 'comet'
env.key_filename = 'comet.key'
env.colorize_errors = True
env.skip_bad_hosts = True
env.combine_stderr = False
node_root_path = '/home/comet/'
local_path = os.getcwd() + "/"
path = "/var/log/comet-straas"

update_result_path = local_path + 'update_result_list/'

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO, filename='update_check.log')
LOG = logging.getLogger(__name__)


def time_decorator(msg):
    """
    Decorates `msg` with current timestamp
    Args:
        msg(str): The log message from fabric
    Returns:
        str: Original message prepended with current date time
    """
    if "\n" not in msg and msg.strip():
        return "[%s] %s" % (time.asctime(), msg)

    return msg
# Compose original method inside of decorator
_original_flush = OutputLooper._flush
OutputLooper._flush = lambda self, msg: {
    _original_flush(self, time_decorator(msg))
}


def isNullOrEmpty(stri):
    if not stri or stri.isspace():
        return True
    else:
        return False


@runs_once
def update_file_init(az_name):
    if os.path.exists(update_result_path + str(az_name).strip() + "/"):
        shutil.rmtree(update_result_path + str(az_name).strip() + "/")
    os.makedirs(update_result_path + str(az_name).strip() + "/")


def handle_dir(dirPath, mode='c'):
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


@parallel
def update_file(az_name):
    ip = env.host
    if ip == None:
        LOG.info(" the cluster : " + str(az_name) + " have no nodes ")
        return None
    with cd(node_root_path):
        try:
            if not exists(path):
                run('pwd; ls -lrt')
                LOG.info(env.host + " is old node")
                append_file(update_result_path + az_name + "/f_err_too_old_node", ip)
                append_file(update_result_path + az_name + "/all_err_node", ip)
            else:
                ret = sudo('df -h /home/comet | grep "100%" | wc -l')
                if int(ret) >= 1:
                    LOG.error(ip + " -----------disk full")
                    append_file(update_result_path + az_name + "/f_err_disk_full", ip)
                    append_file(update_result_path + az_name + "/all_err_node", ip)
                else:
                    LOG.info(env.host + " update file from "+az_name)
                    stdoutres = sudo("nl /etc/comet.agent/agent.conf | sed -n '/token_tenant_idp/p'").stdout
                    if stdoutres == '':
                        sudo(
                            "sed -i " + "'" + r'/server_call_high_timeout=60/a\\token_request_body={\\\\"auth\\\\": {\\\\"tenantId\\\\":\\\\"%s\\\\", \\\\"passwordCredentials\\\\":{\\\\"username\\\\":\\\\"%s\\\\", \\\\"password\\\\":\\\\"%s\\\\"}}}\\ntoken_auth_url=https://os-identity.vip.ebayc3.com/v2.0/tokens\\ntoken_tenant_id=04630f88baae46f49424ee0af315d769' + "'" + " /etc/comet.agent/agent.conf")
# sudo (r'sed -i "/server_call_high_timeout=60/a\token_request_body={\\\\\"auth\\\\\": {\"tenantId\":\"%s\", \"passwordCredentials\":{\"username\":\"%s\", \"password\":\"%s\"}}}\ntoken_auth_url=https://os-identity.vip.ebayc3.com/v2.0/tokens\ntoken_tenant_id=04630f88baae46f49424ee0af315d769" /etc/comet.agent/agent.conf')

                    put(local_path + 'straas-service/comet.agent/comet/agent/cmd/background.py',
                        '/home/comet/rheos.straas/straas-service/comet.agent/comet/agent/cmd', use_sudo=True)
                    put(local_path + 'straas-service/comet.agent/comet/agent/api/taskmanager.py',
                        '/home/comet/rheos.straas/straas-service/comet.agent/comet/agent/api', use_sudo=True)
                    put(local_path + 'straas-service/comet.agent/comet/agent/common/utils.py',
                        '/home/comet/rheos.straas/straas-service/comet.agent/comet/agent/common', use_sudo=True)
                    put(local_path + 'straas-service/comet.agent/comet/agent/common/cfg.py',
                        '/home/comet/rheos.straas/straas-service/comet.agent/comet/agent/common', use_sudo=True)
                    put(local_path + 'straas-service/comet.agent/comet/agent/manager/manager.py',
                        '/home/comet/rheos.straas/straas-service/comet.agent/comet/agent/manager', use_sudo=True)

                    # put(local_path + 'straas-service/comet.core/comet/core/common/config.py',
                    #     '/home/comet/rheos.straas/straas-service/comet.core/comet/core/common', use_sudo=True)
                    # put(local_path + 'straas-service/comet.core/comet/core/common/fs/fs_handler.py',
                    #     '/home/comet/rheos.straas/straas-service/comet.core/comet/core/common/fs', use_sudo=True)
                    # put(local_path + 'straas-service/comet.core/comet/core/common/git/git_handler.py',
                    #     '/home/comet/rheos.straas/straas-service/comet.core/comet/core/common/git', use_sudo=True)
                    # put(local_path + 'straas-service/comet.core/comet/core/common/guest/client/api.py',
                    #     '/home/comet/rheos.straas/straas-service/comet.core/comet/core/common/guest/client', use_sudo=True)
                    # put(local_path + 'straas-service/comet.core/comet/core/common/orc/nova/orc_nova.py',
                    #     '/home/comet/rheos.straas/straas-service/comet.core/comet/core/common/orc/nova', use_sudo=True)
                    # put(local_path + 'straas-service/comet.core/comet/core/common/udns/udnsclient.py',
                    #     '/home/comet/rheos.straas/straas-service/comet.core/comet/core/common/udns', use_sudo=True)
                    # put(local_path + 'straas-service/comet.core/comet/core/common/wsgi.py',
                    #     '/home/comet/rheos.straas/straas-service/comet.core/comet/core/common', use_sudo=True)
                    # put(local_path + 'straas-service/comet.core/comet/core/init/inst.py',
                    #     '/home/comet/rheos.straas/straas-service/comet.core/comet/core/init', use_sudo=True)
                    # put(local_path + 'straas-service/comet.core/comet/core/taskmanager/api.py',
                    #     '/home/comet/rheos.straas/straas-service/comet.core/comet/core/taskmanager', use_sudo=True)
                    # put(local_path + 'straas-service/comet.core/comet/core/taskmanager/background.py',
                    #     '/home/comet/rheos.straas/straas-service/comet.core/comet/core/taskmanager', use_sudo=True)
                    # put(local_path + 'straas-service/comet.server/comet/straas/taskmanager/api.py',
                    #     '/home/comet/rheos.straas/straas-service/comet.server/comet/straas/taskmanager', use_sudo=True)
                    # put(local_path + 'straas-service/comet.server/comet/straas/taskmanager/manager.py',
                    #     '/home/comet/rheos.straas/straas-service/comet.server/comet/straas/taskmanager', use_sudo=True)
                    # put(local_path + 'straas-service/comet.server/comet/straas/web/api.py',
                    #     '/home/comet/rheos.straas/straas-service/comet.server/comet/straas/web', use_sudo=True)
                    # put(local_path + 'straas-service/comet.server/comet/straas/web/service.py',
                    #     '/home/comet/rheos.straas/straas-service/comet.server/comet/straas/web', use_sudo=True)
                    # put(local_path + 'straas-service/comet.core/comet/core/common/orc/nova/orc_nova.py',
                    #     '/home/comet/rheos.straas/straas-service/comet.core/comet/core/common/orc/nova', use_sudo=True)

                    put(local_path + 'agent/api_key', '/home/straas', use_sudo=True)
                    put(local_path + 'agent/api_secret', '/home/straas', use_sudo=True)
                    put(local_path + 'script/restartService.sh', node_root_path, use_sudo=True)
                    sudo('chmod u+x restartService.sh')
                    sudo('./restartService.sh')
                    append_file(update_result_path+az_name+"/update_file_success", ip)
        except SSHException, sshe:
            LOG.error(ip + " -----------cant ssh")
            append_file(update_result_path + az_name + "/f_err_network", ip)
            append_file(update_result_path + az_name + "/all_err_node", ip)
        except NetworkError, nwe:
            LOG.error(ip + " -----------cant ssh")
            append_file(update_result_path + az_name + "/f_err_network", ip)
            append_file(update_result_path + az_name + "/all_err_node", ip)
        except DiskFullException, dfe:
            LOG.error(ip + " -----------disk full")
            append_file(update_result_path + az_name + "/f_err_disk_full", ip)
            append_file(update_result_path + az_name + "/all_err_node", ip)
        except CommandTimeout, ctt:
            LOG.error(ip + "-----------cmd timeout")
            append_file(update_result_path + az_name + "/f_err_cmd_timeout", ip)
            append_file(update_result_path + az_name + "/all_err_node", ip)
        except RuntimeError, re:
            LOG.error(ip + " -----------runtime err")
            append_file(update_result_path + az_name + "/f_err_runtime", ip)
            append_file(update_result_path + az_name + "/all_err_node", ip)
        except BaseException, e:
            LOG.error(ip + " -----------error in verify host, msg: " + str(e) + " " + str(type(e)))
            append_file(update_result_path + az_name + "/f_err_base", ip)
            append_file(update_result_path + az_name + "/all_err_node", ip)


@runs_once
def set_env(file):
    env.timeout = 30
    env.command_timeout = 600
    # cluster_ip_list = cwd + "/" + vpc_name + "_" + az_name
    with open(file, 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            line = row['fqdn']
            env.hosts.append(line.strip())


def append_file(log_file, ip):
    LOG.debug(ip + " append to " + log_file)
    with open(log_file, "a") as f:
        f.write(ip + "\n")
    return True


class DiskFullException(Exception):
    pass