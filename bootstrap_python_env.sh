#!/usr/bin/env bash

HERE=`pwd`
cd /tmp
wget http://www.python.org/ftp/python/2.7.5/Python-2.7.5.tgz /tmp
tar -zxvf Python-2.7.5.tgz
cd Python-2.7.5
mkdir $HERE/.python
./configure --prefix=$HERE/.python
make
make install
cd /tmp
wget --no-check-certificate https://pypi.python.org/packages/source/v/virtualenv/virtualenv-1.11.6.tar.gz
tar -zxvf virtualenv-1.11.6.tar.gz
cd virtualenv-1.11.6/
$HERE/.python/bin/python setup.py install
cd $HERE
$HERE/.python/bin/python /tmp/virtualenv-1.11.6/virtualenv.py .env -p $HERE/.python/bin/python2.7
