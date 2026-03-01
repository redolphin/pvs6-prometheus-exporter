# PVS6 Prometheus Exporter

## Description

## Installation
```
export PVS6_IP=192.168.1.100
export PVS6_SN=ZN1234567890
export POLLING_INTERVAL=30
export EXPORTER_PORT=8000

docker run -d --name pvs6-exporter -e PVS6_IP=192.168.1.100 -e PVS6-SN=ZN1234567890 -p 8000:8000 redolphin/pvs6-prometheus-exporter:main 
```
