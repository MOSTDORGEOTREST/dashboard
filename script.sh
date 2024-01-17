docker system prune -a -f
docker rm $(docker ps -a -q) -f
docker rmi $(docker images -a -q) -f
cd /home/user_bot/dashbord
git pull
sudo service docker restart
docker-compose up