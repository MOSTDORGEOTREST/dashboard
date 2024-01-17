docker system prune -af
docker rm $(docker ps -a -q) -f
docker rmi $(docker images -a -q) -f

sudo rm -rf /var/log/*

cd /home/user_bot/dashbord
git pull
sudo service docker restart
docker-compose up -d

docker-compose -f /home/user_bot/dockprom/docker-compose.yml up -d