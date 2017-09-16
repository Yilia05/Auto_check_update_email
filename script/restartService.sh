#!/bin/bash
cd /home/comet
service comet.agent stop
process_num=`ps aux | grep comet-straas-agent.py  | grep -v grep | wc -l`
if [ "$process_num" -ne 0 ]; then
  echo "service stop ,but comet-straas-agent.py process don't stop"
  ps -ef | grep comet-straas-agent.py | grep -v grep | cut -c 9-15 | xargs kill -s 9
fi
process_num=`ps aux | grep comet-straas-agent.py  | grep -v grep | wc -l`
if [ "$process_num" -eq 0 ]; then
  echo "all comet-straas-agent.py process stop "
fi

if [ -f /etc/comet.agent/agent.conf ]; then
	big_log=`find /var/log/comet-straas/straas-agent.log -size +100M | wc -l`
	
	if [ "$big_log" -ne 0 ]; then
	  rm -rf /var/log/comet-straas/straas-agent.log
	fi
fi

service comet.agent start


