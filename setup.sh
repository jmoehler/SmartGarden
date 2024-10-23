# depending on your system, you may need to install some dependencies
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "\033[0;33m[SETUP]\033[0m You seem to be working on a \033[1;32mLinux\033[0m system!"
    echo "\033[0;33m[SETUP]\033[0m \033[1;37mInstalling system dependencies...\033[0m"
    
    # install tmux
    sudo apt-get install tmux
    if [ $? -ne 0 ]
    then
        echo "\033[0;33m[SETUP]\033[0m \033[0;31mInstalling tmux failed! Exiting setup routine...\033[0m"
        echo "\033[0;33m[SETUP]\033[0m \033[1;31mSetup aborted! \033[0m"
        exit 1
    fi

    # install mysql
    sudo apt-get install mysql-server mysql-client
    if [ $? -ne 0 ]
    then
        echo "\033[0;33m[SETUP]\033[0m \033[0;31mInstalling mysql failed! Exiting setup routine...\033[0m"
        echo "\033[0;33m[SETUP]\033[0m \033[1;31mSetup aborted! \033[0m"
        exit 1
    else 
        echo "\033[0;33m[SETUP]\033[0m \033[0;32mInstalling system dependencies successful!\033[0m"
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "\033[0;33m[SETUP]\033[0m You seem to be working on a \033[1;32mMacOS\033[0m system!"
    echo "\033[0;33m[SETUP]\033[0m \033[1;37mInstalling system dependencies...\033[0m"

    # install tmux
    brew install tmux
    if [ $? -ne 0 ]
    then
        echo "\033[0;33m[SETUP]\033[0m \033[0;31mInstalling tmux failed! Exiting setup routine...\033[0m"
        echo "\033[0;33m[SETUP]\033[0m \033[1;31mSetup aborted! \033[0m"
        exit 1
    fi

    # install mysql
    brew install mysql
    if [ $? -ne 0 ]
    then
        echo "\033[0;33m[SETUP]\033[0m \033[0;31mInstalling mysql failed! Exiting setup routine...\033[0m"
        echo "\033[0;33m[SETUP]\033[0m \033[1;31mSetup aborted! \033[0m"
        exit 1
    else 
        echo "\033[0;33m[SETUP]\033[0m \033[0;32mInstalling system dependencies successful!\n\033[0m"
    fi
fi

# kill all existing mysql processes
echo "\033[0;33m[SETUP]\033[0m \033[1;37mSetting up database...\033[0m"
echo "\033[0;33m[SETUP]\033[0m Checking for existing mysql processes..."
pid=$(ps aux | grep mysql | grep -v grep | awk '{print $2}')
if [ -z "$pid" ]
then
    echo "\033[0;33m[SETUP]\033[0m No existing mysql processes found!"
else
    echo "\033[0;33m[SETUP]\033[0m Found existing mysql processes!"
    for i in $(echo $pid | tr " " "\n")
    do
        kill -9 $i
        echo "\033[0;33m[SETUP]\033[0m Killed process with pid $i"
    done
fi

# start mysql server
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "\033[0;33m[SETUP]\033[0m Starting mysql server..."
    sudo service mysql start > /dev/null 2>&1
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "\033[0;33m[SETUP]\033[0m Starting mysql server..."
    mysql.server start > /dev/null 2>&1
fi


# set correct login
# first try without password, then with default password
echo "\033[0;33m[SETUP]\033[0m Setting correct login..."
echo "\033[0;33m[SETUP]\033[0m Trying access to DB without password..."
sleep 3
mysql -u root -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'root'; FLUSH PRIVILEGES;" > /dev/null 2>&1
if [ $? -ne 0 ]
then
    echo "\033[0;33m[SETUP]\033[0m Login failed, trying with password..."
    mysql -u root -proot -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'root'; FLUSH PRIVILEGES;" > /dev/null 2>&1

    if [ $? -ne 0 ]
    then
        echo "\033[0;33m[SETUP]\033[0m Login failed, exiting setup routine..."
        echo "\033[0;33m[SETUP]\033[0m Please try to set the correct login manually"
        echo "\033[0;33m[SETUP]\033[0m \033[1;31mSetup aborted! \033[0m"
        exit 1
    else
        echo "\033[0;33m[SETUP]\033[0m Login with default password successful!"
        echo "\033[0;33m[SETUP]\033[0m New login credentials:"
        echo "\033[0;33m[SETUP]\033[0m \033[1;30mUsername: root\033[0m"
        echo "\033[0;33m[SETUP]\033[0m \033[1;30mPassword: root\033[0m"
    fi
fi

# reset database
echo "\033[0;33m[SETUP]\033[0m Resetting DB (removing old databases)..."
databases=$(mysql -uroot -proot -e "SHOW DATABASES" -s -N 2>/dev/null | egrep -v "mysql|information_schema|performance_schema|sys")
if [ -z "$databases" ]
then
    echo "\033[0;33m[SETUP]\033[0m No old databases found!"
else
    echo "\033[0;33m[SETUP]\033[0m Found databases to remove!"
    for i in $(echo $databases | tr " " "\n")
    do
        mysql -uroot -proot -e "DROP DATABASE $i" > /dev/null 2>&1
        echo "\033[0;33m[SETUP]\033[0m Removed database $i"
    done
fi
echo "\033[0;33m[SETUP]\033[0m \033[0;32mDatabase setup successful!\n\033[0m"

# install python dependencies
echo "\033[0;33m[SETUP]\033[0m \033[1;37mInstalling python dependencies...\033[0m"
pip3 install -r requirements.txt
if [ $? -ne 0 ]
then
    echo "\033[0;33m[SETUP]\033[0m \033[0;31mInstalling python dependencies failed! Exiting setup routine...\033[0m"
    echo "\033[0;33m[SETUP]\033[0m \033[1;31mSetup aborted! \033[0m"
    exit 1
else
    echo "\033[0;33m[SETUP]\033[0m \033[0;32mInstalling python dependencies successful!\n\033[0m"
fi

echo "\033[0;33m[SETUP]\033[0m \033[1;32mSetup successful! \033[0m"

