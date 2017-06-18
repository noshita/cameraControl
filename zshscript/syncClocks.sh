#!/bin/zsh

# ポートの取得
list_ports=(`gphoto2 --auto-detect | awk -F "  +" '{print $2;}'`)
list_ports=(${list_ports:1:${#list_ports[@]-2}})

# echo $list_ports

# カメラの時間をPCの時間に同期
for port in ${list_ports[@]}; do
	gphoto2 --port $port --set-config datetime=now
done