# Preparing system
sudo apt update
sudo apt upgrade
sudo apt install python3-pip
echo "You should have created oauth_settings.yml already (read documentation). If not, too late. Watch the installation fail!"
sudo pip3 install -r requirements.txt
python3 manage.py migrate

sudo cp tamtt.service /etc/systemd/system/
echo "Service is not automatically enabled. Enable by 'systemctl enable tamtt.service'"
echo "Starting service now"
sudo systemctl start tamtt.service
