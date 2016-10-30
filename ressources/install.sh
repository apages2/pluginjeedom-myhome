touch /tmp/dependancy_myhome_in_progress
echo 0 > /tmp/dependancy_myhome_in_progress
echo "********************************************************"
echo "*             Installation des dépendances             *"
echo "********************************************************"
apt-get update
echo 50 > /tmp/dependancy_myhome_in_progress
apt-get install -y python-serial
echo 100 > /tmp/dependancy_myhome_in_progress
echo "********************************************************"
echo "*             Installation terminée                    *"
echo "********************************************************"
rm /tmp/dependancy_myhome_in_progress
