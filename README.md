# domain-scraper
 
## Installtion
* Copy the env.example to .env and edit the env variables:

  * API="https://registry.scamscan.net/"
  * FIREFOX_PATH="path to firefox executable"
  * NODEID="a random generated uuidv4"
  * IP="" <- leave this blank

* install geckodriver and firefox 
  * sudo apt-get install firefox 
  * Go to the geckodriver releases page. Find the latest version of the driver for your platform and download it https://github.com/mozilla/geckodriver/releases
  * Extract the file with: tar -xvzf geckodriver 
  * Make it executable: chmod +x geckodriver 
  * Add the driver to your PATH so other tools can find it: sudo mv geckodriver /usr/local/bin/
