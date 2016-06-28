#/bin/bash

# Yum安装环境
function yum_install(){
 yum -y install net-snmp-devel  ntp make openssl openssl-devel pcre pcre-devel libpng net-snmp libpng-devel libjpeg-6b libjpeg-devel-6b freetype freetype-devel gd gd-devel zlib zlib-devel gcc gcc-c++ libXpm libXpm-devel ncurses ncurses-devel  libxml2 libxml2-devel imake autoconf automake screen sysstat compat-libstdc++-33 curl curl-devel cmake
}



# 软件包解包函数
function soft_unpack(){
	SOFT_NAME=$1
	if [ -f ${SOFT_NAME} ]
	then
		echo ">>>>现在解压软件包: ${SOFT_NAME}:"
		tar -zxvf ${SOFT_NAME}
	else 
		echo "当前目录找不到软件: ${SOFT_NAME}" 
	fi
}

# Nginx安装及配置函数
function nginx_install(){
    NGINX_NAME=$1
    `which useradd` www -M  && echo "www 用户创建成功!" || echo "www 用户创建失败"
    cd ${NGINX_NAME}
    echo "开始编译Nginx:"
   ./configure --prefix=/opt/nginx --user=www --group=www --with-http_stub_status_module --with-http_ssl_module --with-pcre --with-http_realip_module
    echo "开始安装Nginx:"
    make && make install && echo "Nginx 安装成功" || { echo "Nginx 安装失败,请重试!"; exit 3; }
    cd ..
    # Nginx 配置文件
    cp -f nginx.conf  /opt/nginx/conf/nginx.conf && echo "Nginx 配置写入成功" || { echo "Nginx 配置写入失败,请重试!"; exit 3; }
    # nginx 启动脚本
    cp -f nginx /etc/init.d/nginx && echo "启动脚本写入成功!" || { echo "启动脚本写入失败!请重试"; exit 3; } 
    [ -e /data/logs ] || mkdir -p /data/logs
    [ -e /data/htdocs/html ] || mkdir -p /data/htdocs/html
    chmod 777 /etc/init.d/nginx 
    chkconfig nginx on 
    # 启动Nginx 
    `which service ` nginx start && echo 'Nginx 启动成功!' || { echo 'Nginx 启动失败, 请重试' ; exit 3; }
}

function php_install(){
    PHP_NAME=$1
    # 安装libmcrypt 
    LIBMC_SOFT=`ls | grep  libmcrypt`
    echo ${LIBMC_SOFT}
    if [ -z ${LIBMC_SOFT} ]
    then 
        echo "找不到libmcrypt安装包 请确认后重试"
        exit 3 
    else 
        `which tar` -zxvf ${LIBMC_SOFT}
        cd ${LIBMC_SOFT%%.tar*}
        ./configure --prefix=/opt/libmcrypt
        make && make install 
        cd ..
    fi 
    # 安装libiconv
    LICONV_SOFT=`ls | grep  libiconv`
    echo ${LICONV_SOFT}
    if [ -z ${LICONV_SOFT} ]
    then
        echo "找不到libiconv安装包 请确认后重试"
        exit 3
    else
        `which tar` -zxvf ${LICONV_SOFT}
        cd ${LICONV_SOFT%%.tar*}
        ./configure --prefix=/usr/lib64
        make && make install
        ln -sf /usr/lib64/lib/libiconv.so.2 /usr/lib64/
        ldconfig
        cd ..
    fi

    # 安装php
    cd ${PHP_NAME}
    echo "安装php:"
    ./configure  --prefix=/opt/php7 \
    --with-config-file-path=/opt/php7/etc \
    --with-mcrypt=/opt/libmcrypt \
    --with-mysqli=mysqlnd --with-pdo-mysql=mysqlnd \
    --with-gd --with-iconv --with-zlib --enable-xml --enable-bcmath \
    --enable-shmop --enable-sysvsem --enable-inline-optimization \
    --enable-mbregex --enable-fpm --enable-mbstring --enable-ftp \
    --enable-gd-native-ttf --with-openssl --enable-pcntl \
    --enable-sockets --with-xmlrpc --enable-zip --enable-soap \
    --without-pear --with-gettext --enable-session --with-curl \
    --with-jpeg-dir --with-freetype-dir --enable-opcache
    [ $? -eq 0 ] || { echo "编译失败,脚本退出"; exit 3; } && echo "编译成功" 
    make ZEND_EXTRA_LIBS='-liconv' -j `grep -c 'process' /proc/cpuinfo` && make install || { echo "php 安装失败, 脚本退出"; exit 3; }  && echo 'php 安装成功'
    cd ..
    
    # 修改配置文件
    [ -f ${SCRIPT}/php-fpm.conf ] && cp -f ${SCRIPT}/php-fpm.conf /opt/php7/etc/php-fpm.conf;echo 'php-fpm.conf写入成功' || { echo "当前目录找不到php-fpm.conf, 请手动配置"; exit 3 ; }
    [ -f ${SCRIPT}/php.ini ] && cp -f ${SCRIPT}/php.ini /opt/php7/etc/php.ini;echo 'php.ini写入成功' || { echo "当前目录找不到php.ini, 请手动配置" ; exit 3; }
    [ -f ${SCRIPT}/php-fpm ] && cp -f ${SCRIPT}/php-fpm /etc/init.d/php-fpm ; chmod 777 /etc/init.d/php-fpm ;echo 'php-fpm启动脚本写入成功'|| { echo "当前目录找不到php-fpm, 请手动配置" ; exit 3 ; }
    `which chkconfig ` php-fpm on 

    # 安装redis扩展
    REDIS_NAME=`ls |grep phpredis.*zip`
    unzip ${REDIS_NAME}
    cd ${REDIS_NAME%%.*}
    /opt/php7/bin/phpize 
    ./configure --with-php-config=/opt/php7/bin/php-config
    make && make install && echo "redis扩展 安装成功" || { echo "redis扩展 安装失败" ; exit 3 ; }
    cd ..
    
    # 安装Rabbitmq扩展
    RABBITMQ=`ls |grep rabbitmq-c.*zip`
    unzip ${RABBITMQ}
    cd ${RABBITMQ%%.*}
    [ -e build ] || mkdir build 
    cd build
    cmake -DCMAKE_INSTALL_PREFIX=/opt/rabbitmq .. &&  cmake --build . --target install
    cd ..
    ln -fs /usr/local/lib/lib64/librabbitmq.so.4 /usr/local/lib/ && echo "RabbitMq 安装成功" || { echo "RabbitMq 安装失败"; exit 3 ; }
    cd ..
    
    # 安装amqp扩展
    AMPQ=`ls | grep amqp.*z`
    tar -zxvf ${AMPQ}
    cd `sed -r 's/(\.tgz)|(\.tar\.gz)//g' <<< ${AMPQ}`
    /opt/php7/bin/phpize 
    ./configure --with-php-config=/opt/php7/bin/php-config --with-librabbitmq-dir=/opt/rabbitmq
    ln -sf /opt/rabbitmq/lib64/librabbitmq.so /usr/lib/
    ldconfig
    make && make install && echo "Ampq扩展 安装成功" || { echo "Ampq扩展 安装失败"  ; exit 3 ; }
    cd ..
    
    # 启动php-fpm
    `which service ` php-fpm start
}

function mysql_install() {
    echo "安装Mysql"
    useradd -M mysql 
    cp -f my.cnf /etc/my.cnf
    MYSQL_NAME=$1
    [ -e /data/mysql/ ] || mkdir -p /data/mysql
    [ -e /opt/mysql/ ] || mkdir -p /opt/mysql
    chown mysql.mysql -R /data/mysql/
    echo "拷贝${MYSQL_NAME} 目录到/opt/mysql/"
    cp  -fr ${MYSQL_NAME} /opt/mysql/
    ln -fs /opt/mysql/${MYSQL_NAME} /usr/local/mysql
    cp -fr /usr/local/mysql/support-files/mysql.server /etc/init.d/mysqld 
    chmod 777 /etc/init.d/mysqld
    echo "初始化Mysql"
    /usr/local/mysql/bin/mysqld --initialize-insecure --console --user=mysql --basedir=/usr/local/mysql --datadir=/data/mysql
    echo "启动Mysql"
    service mysqld start 
    [ $? -eq 0 ] && echo "Mysql 启动成功" || { echo "Mysql 启动失败" ; exit 3 ; }
    echo "woca "
}

function zabbix_install(){
    echo "安装Zabbix"
    useradd -M zabbix
    ZABBIX_NAME=$1
    cd ${ZABBIX_NAME}
    if [ -n $2 ] && [  "$2" == "zabbix_server" ]
    then
        ZABBIX_FLAG='--enable-server'
        /usr/local/mysql/bin/mysql -e 'create database zabbix'
        /usr/local/mysql/bin/mysql -e "grant all on zabbix.* to zabbix@localhost identified by 'zabbix'"
        /usr/local/mysql/bin/mysql -uzabbix -pzabbix zabbix < database/mysql/schema.sql
        /usr/local/mysql/bin/mysql -uzabbix -pzabbix zabbix < database/mysql/images.sql
        /usr/local/mysql/bin/mysql -uzabbix -pzabbix zabbix < database/mysql/data.sql
        cp -f misc/init.d/fedora/core/zabbix_server /etc/init.d/
        sed -ri 's#(BASEDIR=).*#\1/opt/zabbix#' /etc/init.d/zabbix_server
        cp -fr frontends/php /data/htdocs/html/zabbix
        chown -R www:www /www/coolnull.com/zabbix
        ln -fs /opt/mysql/${MYSQL_NAME}/lib/libmysqlclient.so.20 /usr/lib/
        ldconfig
        iptables -I INPUT -p tcp  --dport 10050 -j ACCEPT
        iptables -I INPUT -p udp  --dport 10050 -j ACCEPT
    fi
    ./configure --prefix=/opt/zabbix ${ZABBIX_FLAG} --enable-proxy --enable-agent --with-mysql=/usr/local/mysql/bin/mysql_config --with-net-snmp --with-libcurl
    make && make install
    cp -f misc/init.d/fedora/core/zabbix_agentd /etc/init.d/
    sed -ri 's#(BASEDIR=).*#\1/opt/zabbix#' /etc/init.d/zabbix_agentd
    sed -ri 's/# (Timeout=).*/\120/' /opt/zabbix/etc/zabbix_agentd.conf
    iptables -I INPUT -p tcp  --dport 10051 -j ACCEPT
    iptables -I INPUT -p udp  --dport 10051 -j ACCEPT
    cat >> /etc/services <<'eof'
zabbix-agent    10050/tcp                           #ZabbixAgent
zabbix-agent    10050/udp                           #Zabbix Agent
zabbix-trapper  10051/tcp                           #ZabbixTrapper
zabbix-trapper  10051/udp                           #Zabbix Trapper
eof
    [ -z ${ZABBIX_FLAG} ] || sed -ri 's/(^DB[^=]+=).*/\1zabbix/' /opt/zabbix/etc/zabbix_server.conf
    [ -z ${ZABBIX_FLAG} ] || /etc/init.d/zabbix_server start 
    [ -z ${ZABBIX_FLAG} ] || AGENT_IP=127.0.0.1 &&  AGENT_IP=192.168.9.30
    sed -ri "s/(^Serve[^=]+=).*/\1${AGENT_IP}/" /opt/zabbix/etc/zabbix_agentd.conf
    /etc/init.d/zabbix_agentd start  && echo "Zabbix 安装完成并启动成功" || { echo "Zabbix 启动失败!" ; exit 3 ; }
    iptables -I INPUT -p udp --dport 10050:10051 -j ACCEPT
    iptables -I INPUT -p tcp --dport 10050:10051 -j ACCEPT
    chkconfig --add zabbix_agentd


}


LOCAL_IP=$(ifconfig eth0|grep -oP '(?<=inet addr:)\S+')
SCRIPT=`pwd`
select option in Nginx Mysql Php Zabbix All
do
    case $option in 
        Nginx)
            PATTERN='nginx.*gz'
            ;;
        Mysql)
            PATTERN='mysql.*gz'
            ;;
        Php)
            PATTERN='php.*gz'
            ;;
        Zabbix)
            PATTERN='zabbix.*gz'
            ;;
        All)
            PATTERN='(nginx|mysql|php|zabbix).*gz'
            ;;
        *) 
            echo "Please input correct option!"
            ;;
    esac
    SOFT_WARE_LIST=$(ls ${SCRIPT}|grep -iP "${PATTERN}")
    echo $SOFT_WARE_LIST
    break
done

yum_install
# 检查脚本所在目录, 有无软件包: Nginx Mysql Php
if [ -z ${SOFT_WARE_LIST} ]
then
    echo "缺少软件包! (Nginx 或 Php 或 Mysql 或 Zabbix)"
    exit 3
else 
    for TMP in ${SOFT_WARE_LIST}
    do
        soft_unpack ${TMP}
        SOFT_NAME=${TMP%%.tar*}  # 去后缀
        case ${TMP%%-*} in
            nginx)
                nginx_install ${SOFT_NAME}
                ;;
            php)
                php_install ${SOFT_NAME}
                ;;
            mysql)
                mysql_install ${SOFT_NAME}
                ;;
            zabbix)
                zabbix_install ${SOFT_NAME} $1
                ;;
                *)
                echo "No Nginx"
                ;;
        esac
            
    done
fi
echo "LNMP + Zabbix $1 部署完毕"
