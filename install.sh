sudo cp microsoft-graph.service /etc/systemd/system/
echo "Service is not automatically enabled. Enable by 'systemctl enable microsoft-graph.service'"
echo "Starting service now"
sudo systemctl start microsoft-graph.service
