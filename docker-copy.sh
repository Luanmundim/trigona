HOSTNAME=$(hostname)
CURRENTDATETIME=$(date +%Y%m%d-%H%M%S)
TARGET_DIR="/home/ubuntu/${HOSTNAME}-${CURRENTDATETIME}-log"
docker cp trigona:/home/scripts/log "$TARGET_DIR"
