#! /usr/bin/bash
source ./influxdbDetails.conf

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

check_telegraf()
{
    add_grafana_repo
    yum install telegraf -y
    sed -i '/# \[\[inputs.net\]\]/s/^#//g' /etc/telegraf/telegraf.conf
    sed -i '/# \[\[inputs.netstat\]\]/s/^#//g' /etc/telegraf/telegraf.conf
    sed -i "/\[\[outputs.influxdb\]\]/aurls = [\"http://$url:8086\"]\ndatabase = \"$database\"\nusername = \"$username\"\npassword = \"$password\"" /etc/telegraf/telegraf.conf
    systemctl enable telegraf
    systemctl start telegraf
    systemctl restart telegraf
}

check_telegraf

