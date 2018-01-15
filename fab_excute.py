import subprocess
import logging
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO, filename='update_check.log')
LOG = logging.getLogger(__name__)

p1 = subprocess.Popen("fab -f update.py update_file_init:lvs01 set_env:./dev_lvs01/cluster_ip_list/error_fqdn_list "
                      "update_file:lvs01", shell=True)
p2 = subprocess.Popen("fab -f update.py update_file_init:lvs02 set_env:./dev_lvs02/cluster_ip_list/error_fqdn_list "
                      "update_file:lvs02", shell=True)
p3 = subprocess.Popen("fab -f update.py update_file_init:slc01 set_env:./dev_slc01/cluster_ip_list/error_fqdn_list "
                      "update_file:slc01", shell=True)
p4 = subprocess.Popen("fab -f update.py update_file_init:slc07 set_env:./dev_slc07/cluster_ip_list/error_fqdn_list "
                      "update_file:slc07", shell=True)
p5 = subprocess.Popen("fab -f update.py update_file_init:phx01 set_env:./dev_phx01/cluster_ip_list/error_fqdn_list "
                      "update_file:phx01", shell=True)
p6 = subprocess.Popen("fab -f update.py update_file_init:phx02 set_env:./dev_phx02/cluster_ip_list/error_fqdn_list "
                      "update_file:phx02", shell=True)

ps1 = subprocess.Popen("fab -f update.py update_file_init:staging_lvs01 set_env:./rheosBehaviorStaging_lvs01/cluster_ip_list/error_fqdn_list "
                       "update_file:staging_lvs01", shell=True)
ps2 = subprocess.Popen("fab -f update.py update_file_init:staging_lvs02 set_env:./rheosBehaviorStaging_lvs02/cluster_ip_list/error_fqdn_list "
                       "update_file:staging_lvs02", shell=True)
ps3 = subprocess.Popen("fab -f update.py update_file_init:staging_phx01 set_env:./rheosBehaviorStaging_phx01/cluster_ip_list/error_fqdn_list "
                       "update_file:staging_phx01", shell=True)
ps4 = subprocess.Popen("fab -f update.py update_file_init:staging_phx02 set_env:./rheosBehaviorStaging_phx02/cluster_ip_list/error_fqdn_list "
                       "update_file:staging_phx02", shell=True)
ps5 = subprocess.Popen("fab -f update.py update_file_init:staging_slc01 set_env:./rheosBehaviorStaging_slc01/cluster_ip_list/error_fqdn_list "
                       "update_file:staging_slc01", shell=True)
ps6 = subprocess.Popen("fab -f update.py update_file_init:staging_slc07 set_env:./rheosBehaviorStaging_slc07/cluster_ip_list/all_fqdn_id_list "
                       "update_file:staging_slc07", shell=True)

p1.wait()
p2.wait()
p3.wait()
p4.wait()
p5.wait()
p6.wait()

ps1.wait()
ps2.wait()
ps3.wait()
ps4.wait()
ps5.wait()
ps6.wait()

print "update success"
