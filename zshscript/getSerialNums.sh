#!/bin/zsh

OUTPUT_PATH=$1

# ポートの取得
list_ports=(`gphoto2 --auto-detect | awk -F "  +" '{print $2;}'`)
list_ports=(${list_ports:1:${#list_ports[@]-2}})

# シリアルナンバーの取得
list_serialnum=()
for port in ${list_ports[@]}; do
	list_serialnum=($list_serialnum `gphoto2 --port $port --get-config eosserialnumber | ggrep -oP "\d+"`)
done
# 出力
for serialnum in ${list_serialnum[@]}; do
	echo $serialnum
done
