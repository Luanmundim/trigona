screen -ls | grep qeeqbox | cut -d. -f1 | awk '{print }' | xargs kill
echo "Qeeqbox foi pausado."
