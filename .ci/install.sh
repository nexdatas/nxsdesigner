#!/usr/bin/env bash

echo "restart mysql service"
if [ "$1" = "debian11" ] || [ "$1" = "debian12" ]  || [ "$1" = "debian13" ] || [ "$1" = "ubuntu24.04" ] || [ "$1" = "ubuntu26.10py" ] || [ "$1" = "ubuntu25.04" ] || [ "$1" = "ubuntu26.04" ]; then
    docker exec --user root ndts service mariadb restart
else
    # workaround for a bug in debian9, i.e. starting mysql hangs
    docker exec --user root ndts service mysql stop
    if [ "$1" = "ubuntu20.04" ] || [ "$1" = "ubuntu20.10" ] || [ "$1" = "ubuntu21.04" ] || [ "$1" = "ubuntu22.04" ] ; then
	docker exec --user root ndts /bin/bash -c 'usermod -d /var/lib/mysql/ mysql'
    fi
    # docker exec  --user root ndts /bin/bash -c '$(service mysql start &) && sleep 30'
    docker exec --user root ndts service mysql start
fi

docker exec --user root ndts chown -R tango:tango .

echo "install tango-common"
docker exec  --user root ndts /bin/bash -c 'apt-get -qq update; export DEBIAN_FRONTEND=noninteractive; apt-get -qq install -y tango-common; sleep 10'
if  [ "$1" = "ubuntu24.04" ] || [ "$1" = "ubuntu24.10" ] || [ "$1" = "ubuntu25.04" ] || [ "$1" = "ubuntu26.04" ]; then
    # docker exec  --user tango ndts /bin/bash -c '/usr/lib/tango/DataBaseds 2 -ORBendPoint giop:tcp::10000  &'
    docker exec  --user root ndts /bin/bash -c 'echo -e "[client]\nuser=root\npassword=rootpw" > /root/.my.cnf'
    docker exec  --user root ndts /bin/bash -c 'echo -e "[client]\nuser=tango\nhost=localhost\npassword=rootpw" > /var/lib/tango/.my.cnf'
    docker exec  --user root ndts /usr/bin/mysql -e 'GRANT ALL PRIVILEGES ON tango.* TO "tango"@"%" identified by "rootpw"'
    docker exec  --user root ndts /usr/bin/mysql -e 'GRANT ALL PRIVILEGES ON tango.* TO "tango"@"localhost" identified by "rootpw"'
    docker exec  --user root ndts /usr/bin/mysql -e 'FLUSH PRIVILEGES'
fi
if [ "$1" = "ubuntu20.04" ] || [ "$1" = "ubuntu20.10" ] || [ "$1" = "ubuntu21.04" ] || [ "$1" = "ubuntu21.10" ] || [ "$1" = "ubuntu22.04" ]; then
    # docker exec  --user tango ndts /bin/bash -c '/usr/lib/tango/DataBaseds 2 -ORBendPoint giop:tcp::10000  &'
    docker exec  --user root ndts /bin/bash -c 'echo -e "[client]\nuser=root\npassword=rootpw" > /root/.my.cnf'
    docker exec  --user root ndts /bin/bash -c 'echo -e "[client]\nuser=tango\nhost=127.0.0.1\npassword=rootpw" > /var/lib/tango/.my.cnf'
fi
if   [ "$1" = "ubuntu26.10py" ]; then
    # docker exec  --user tango ndts /bin/bash -c '/usr/lib/tango/DataBaseds 2 -ORBendPoint giop:tcp::10000  &'
    docker exec  --user root ndts /bin/bash -c 'echo -e "[client]\nuser=root\npassword=rootpw" > /root/.my.cnf'
    docker exec  --user tango ndts /bin/bash -c 'echo -e "[client]\nuser=tango\nhost=localhost\npassword=rootpw" > /var/lib/tango/.my.cnf'
    docker exec  --user tango ndts /bin/bash -c 'echo -e "[client]\nuser=tango\nhost=localhost\npassword=rootpw" > /home/tango/.my.cnf'
    # docker exec  --user root ndts /bin/bash -c 'echo -e "[client]\nuser=tango\nhost=127.0.0.1\npassword=rootpw" > /var/lib/tango/.my.cnf'
    docker exec  --user root ndts /usr/bin/mysql -e 'GRANT ALL PRIVILEGES ON tango.* TO "tango"@"%" identified by "rootpw"'
    docker exec  --user root ndts /usr/bin/mysql -e 'GRANT ALL PRIVILEGES ON tango.* TO "tango"@"localhost" identified by "rootpw"'
    docker exec  --user root ndts /usr/bin/mysql -e 'FLUSH PRIVILEGES'
    docker exec --user tango ndts /usr/bin/bash  -c 'pwd'
    docker exec --user tango ndts /usr/bin/bash  -c 'echo "$TANGO_HOST"'
    docker exec --user tango ndts /usr/bin/mysql -e 'show databases;'
fi
echo "install tango-db"
docker exec  --user root ndts /bin/bash -c 'apt-get -qq update; export DEBIAN_FRONTEND=noninteractive; apt-get -qq install -y tango-db; sleep 10'
if [ "$?" -ne "0" ]; then exit 255; fi
if  [ "$1" = "ubuntu24.04" ] || [ "$1" = "ubuntu24.10" ] || [ "$1" = "ubuntu25.04" ] || [ "$1" = "ubuntu26.04" ]; then
    docker exec  --user tango ndts /usr/bin/mysql -e 'create database tango'
    docker exec  --user tango ndts /bin/bash -c '/usr/bin/mysql tango < /usr/share/dbconfig-common/data/tango-db/install/mysql'
fi

if   [ "$1" = "ubuntu26.10py" ] ; then
    # docker exec --user root ndts systemctl restart tango-db.service
    # docker exec --user root ndts systemctl status tango-db.service
    # echo "restart tango-db"
    # docker exec  --user root ndts service tango-db restart
    # echo "start tango-db"
    # docker exec  --user root ndts service tango-db start
    # echo "status tango-db"
    # docker exec  --user root ndts service tango-db status
    # docker exec  --user root ndts /bin/bash -c 'ps -ef | grep Databaseds'
    # docker exec  --user root ndts /bin/bash -c 'ps -ef | grep tango'
    # echo "start databaseds"
    docker exec  --user tango ndts /bin/bash -c '/usr/lib/tango/Databaseds 2   -ORBendPoint giop:tcp::10000  &'
    docker exec  --user root ndts /bin/bash -c 'ps -ef | grep Databaseds'
    docker exec  --user root ndts /bin/bash -c 'ps -ef | grep tango'
else
    docker exec  --user root ndts service tango-db restart
fi


echo "install tango servers"
docker exec  --user root ndts /bin/bash -c 'apt-get -qq update; export DEBIAN_FRONTEND=noninteractive;  apt-get -qq install -y  tango-starter tango-test liblog4j1.2-java'
if [ "$?" -ne "0" ]; then exit 255; fi

docker exec --user root ndts service tango-starter restart

docker exec  --user root ndts chown -R tango:tango .


docker exec  --user root ndts /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update; apt-get -qq install -y xvfb  libxcb1 libx11-xcb1 libxcb-keysyms1 libxcb-image0 libxcb-icccm4 libxcb-render-util0 xkb-data'
if [ "$?" -ne "0" ]; then exit 255; fi

docker exec  --user root ndts mkdir -p /tmp/runtime-tango
docker exec  --user root ndts chown -R tango:tango /tmp/runtime-tango

echo "install tango servers"
docker exec  --user root ndts /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update;  apt-get -qq install -y  tango-starter tango-test liblog4j1.2-java pyqt5-dev-tools'
if [ "$?" -ne "0" ]; then exit 255; fi


if   [ "$1" = "ubuntu26.10py" ] ; then
    # echo "restart tango-starter"
    # docker exec --user root ndts service tango-starter restart
    # echo "start tango-starter"
    # docker exec --user root ndts service tango-starter start
    echo "status tango-starter"
    docker exec --user root ndts service tango-starter status
    docker exec  --user root ndts /bin/bash -c 'ps -ef | grep Starter'
    echo "start  STARTER"
    docker exec  --user tango ndts /bin/bash -c '/usr/bin/tango_admin --add-server Starter/$(hostname) Starter tango/admin/$(hostname)'
    docker exec  --user tango ndts /bin/bash -c '/usr/lib/tango/Starter $(hostname) &'
    docker exec  --user root ndts /bin/bash -c 'ps -ef | grep Starter'
    # docker exec --user root ndts systemctl restart tango-starter.service
    # docker exec --user root ndts systemctl status tango-starter.service
    # docker exec  --user root ndts service tango-db status
else
    docker exec --user root ndts service tango-starter restart
fi

if [ "$?" -ne "0" ]; then exit -1; fi
echo "start Xvfb :99 -screen 0 1024x768x24 &"
docker exec  --user root ndts /bin/bash -c 'export DISPLAY=":99.0"; Xvfb :99 -screen 0 1024x768x24 &'
if [ "$?" -ne "0" ]; then exit 255; fi

echo "install python-pytango"
docker exec  --user root ndts /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update; apt-get -qq install -y'
if [ "$?" -ne "0" ]; then exit 255; fi




if [ "$2" = "2" ]; then
    echo "install pytango and nxsconfigserver-db"
    docker exec  --user root ndts /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update; apt-get install -y   python-pytango  nxsconfigserver-db ; sleep 10'
else
    if [ "$1" = "debian10" ] || [ "$1" = "ubuntu24.04" ] || [ "$1" = "ubuntu26.10py" ] || [ "$1" = "ubuntu25.04" ] || [ "$1" = "ubuntu26.04" ] || [ "$1" = "ubuntu22.04" ] || [ "$1" = "ubuntu20.04" ] || [ "$1" = "ubuntu20.10" ] || [ "$1" = "debian11" ] || [ "$1" = "debian12" ]  || [ "$1" = "debian13" ] ; then
	echo "install pytango"
	docker exec --user root ndts /bin/bash -c 'apt-get -qq update; apt-get install -y   python3-tango'
	echo "install nxsconfigserver-db"
	docker exec --user root ndts /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive;  apt-get -qq update; apt-get  install -y   nxsconfigserver-db'
	if [ "$1" = "ubuntu24.04" ] || [ "$1" = "ubuntu24.10" ] || [ "$1" = "ubuntu25.04" ]; then
	    docker exec  --user root ndts /usr/bin/mysql -e 'GRANT ALL PRIVILEGES ON nxsconfig.* TO "tango"@"%" identified by "rootpw"'
	    docker exec  --user root ndts /usr/bin/mysql -e 'GRANT ALL PRIVILEGES ON nxsconfig.* TO "tango"@"localhost" identified by "rootpw"'
	    docker exec  --user root ndts /usr/bin/mysql -e 'FLUSH PRIVILEGES'
	    docker exec  --user tango ndts /usr/bin/mysql -e 'create database nxsconfig'
	    docker exec  --user tango ndts /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; /usr/bin/mysql nxsconfig < /usr/share/dbconfig-common/data/nxsconfigserver-db/install/mysql'
	fi
	if [ "$1" = "ubuntu26.10py" ]; then
	    docker exec  --user root ndts /usr/bin/mysql -e 'GRANT ALL PRIVILEGES ON nxsconfig.* TO "tango"@"%" identified by "rootpw"'
	    docker exec  --user root ndts /usr/bin/mysql -e 'GRANT ALL PRIVILEGES ON nxsconfig.* TO "tango"@"localhost" identified by "rootpw"'
	    docker exec  --user root ndts /usr/bin/mysql -e 'FLUSH PRIVILEGES'
	fi
    else
	echo "install pytango and nxsconfigserver-db"
	docker exec  --user root ndts /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive;  apt-get -qq update; apt-get -qq install -y   python3-pytango nxsconfigserver-db; sleep 10'
    fi
fi
if [ "$?" != "0" ]; then exit 255; fi


echo "install nxs packages"
if [ "$2" = "2" ]; then
    echo "install python-pytango"
    docker exec --user root ndts /bin/bash -c 'apt-get -qq update; apt-get install -y python-nxsconfigserver python-nxswriter python-pyqt5  python-nxstools  python-setuptools; sleep 10'
else
    docker exec --user root ndts /bin/bash -c 'apt-get -qq update; apt-get install -y python3-nxsconfigserver python3-nxswriter python3-pyqt5  python3-nxstools python3-setuptools; sleep 10'
fi
if [ "$?" != "0" ]; then exit 255; fi

if [ "$2" = "2" ]; then
    echo "install nxsconfigtool"
    docker exec  ndts python setup.py build
    docker exec --user root ndts python setup.py  install
else
    echo "install nxsconfigtool3"
    docker exec --user root ndts chown -R tango:tango .
    docker exec ndts mkdir build
    if [ "$1" = "ubuntu22.04" ] ; then
	docker exec --user root ndts python3 -m pip install . -vv  --no-deps --no-build-isolation
    else
	docker exec --user root ndts python3 -m pip install . -vv  --no-deps --no-build-isolation  --break-system-packages --root-user-action=ignore
    fi    
    # if [ "$?" != "0" ]; then exit 255; fi

    echo "build python3-nxstools docs"
    docker exec ndts mkdir doc/_static
    docker exec ndts sphinx-build  doc build/sphinx/html
fi
if [ "$1" != "ubuntu26.04" ] && [ "$1" != "ubuntu26.04py" ] && [ "$?" != "0" ]; then exit 255; fi

if  [ "$1" = "debian13py" ] || [ "$1" = "ubuntu26.04py" ] || [ "$1" = "ubuntu26.10py" ] ; then
    echo "remove python3-mysqldb"
    docker exec  --user root ndts /bin/bash -c 'apt-get  install -y   python3-pymysql'
    docker exec  --user root ndts /bin/bash -c 'apt-get  remove -y   python3-mysqldb'
fi
