#!/usr/bin/env bash
echo "tasks start running"
echo "crawling all node "
python crawl_all.py
echo "check all node "
python check_status.py
echo "update wrong node "
python fab_excute.py
echo "check again "
python check_status.py
echo "email to manager"
python email_to_manager.py