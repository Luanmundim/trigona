screen -ls | grep tcpdump | cut -d. -f1 | awk '{print }' | xargs kill
echo "Script de monitoramento utilizando TCPDUMP foi pausado."
