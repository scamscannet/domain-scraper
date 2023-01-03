# domain-scraper
 
* Copy the env.example to .env

API="https://registry.scamscan.net/"
FIREFOX_PATH="path_to_firefox"
NODEID="UUIDv4"
IP=""

* install geckodriver and firefox

sudo apt-get install firefox

Go to the geckodriver releases page. Find the latest version of the driver for your platform and download it https://github.com/mozilla/geckodriver/releases . For example:
wget link

Extract the file with:
tar -xvzf geckodriver*

Make it executable:
chmod +x geckodriver

Add the driver to your PATH so other tools can find it:
sudo mv geckodriver /usr/local/bin/
