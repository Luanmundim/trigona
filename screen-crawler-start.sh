screen -ls | grep crawler | cut -d. -f1 | awk '{print $1}' | xargs kill

screen -dmS crawler bash -c 'sudo python3 /home/scripts/crawler/crawler.py'
echo "Script de monitoramento crawler foi iniciado!"

# Kill the screen session after the script has completed
#screen -S crawler -X quit
echo "Script de monitoramento crawler foi finalizado!"
