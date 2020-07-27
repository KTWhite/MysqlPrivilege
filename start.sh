#!/bin/sh
cd /opt/python/python
pm2 start $pyscript
pm2 logs 0