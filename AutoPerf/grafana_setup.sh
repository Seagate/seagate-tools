#!/bin/bash

add_grafana_repo()
{
cat <<EOF | sudo tee /etc/yum.repos.d/influxdb.repo
[influxdb]
name = InfluxDB Repository - RHEL \$releasever
baseurl = https://repos.influxdata.com/rhel/\$releasever/\$basearch/stable
enabled = 1
gpgcheck = 1
gpgkey = https://repos.influxdata.com/influxdb.key
EOF
}

add_grafana_repo
wget https://dl.grafana.com/oss/release/grafana-7.1.1-1.x86_64.rpm
sudo yum install grafana-7.1.1-1.x86_64.rpm -y
sudo yum install influxdb -y
sed -i "/\[http\]/aenable = true \n flux-enabled = false \n bind-address = \":8086\" \n auth-enabled = false" /etc/influxdb/influxdb.conf
sudo systemctl enable influxdb
sudo systemctl enable grafana-server.service
sudo systemctl start influxdb
sudo systemctl start grafana-server.service

