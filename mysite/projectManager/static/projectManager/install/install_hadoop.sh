HADOOP_VERSION=2.7.3
HADOOP_USER=hadoop

sudo adduser $HADOOP_USER

wget http://mirror.apache-kr.org/hadoop/common/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz
tar xvfz hadoop-$HADOOP_VERSION.tar.gz

sudo mv hadoop-$HADOOP_VERSION /usr/local/

cd /usr/local

sudo mkdir hadoop-datastore

sudo chown $HADOOP_USER:$HADOOP_USER hadoop-datastore
sudo chown -R $HADOOP_USER:$HADOOP_USER hadoop-$HADOOP_VERSION 

cd -

sudo sh -c "echo \"export PATH=/usr/local/hadoop-$HADOOP_VERSION/bin:\$PATH\" >> /home/$HADOOP_USER/.bashrc"
sudo chown $HADOOP_USER:$HADOOP_USER /home/$HADOOP_USER/.bashrc

