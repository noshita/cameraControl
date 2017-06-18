#!/bin/zsh

CAMERALIST_PATH=$1
cat $CAMERALIST_PATH| awk -F' *, *' '{print $1 $2;}'

# ポートの取得
list_ports=(`gphoto2 --auto-detect | awk -F "  +" '{print $2;}'`)
list_ports=(${list_ports:1:${#list_ports[@]-2}})

# データのダウンロード
for port in ${list_ports[@]}; do
	gphoto2 --port $port --get-config eosserialnumber
done