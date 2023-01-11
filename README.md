# domain-scraper
 
## Installtion
* Copy the env.example to .env and edit the env variables:

  * API="https://registry.scamscan.net"
  * FIREFOX_PATH="path to firefox executable"
  * NODEID="a random generated uuidv4"
  * IP="" <- leave this blank

* install geckodriver and firefox 
  * sudo apt-get install firefox 
  * Go to the [geckodriver releases page](https://github.com/mozilla/geckodriver/releases). Find the latest version of the driver for your platform and download it
  * Extract the file with: tar -xvzf geckodriver 
  * Make it executable: chmod +x geckodriver 
  * Add the driver to your PATH so other tools can find it: sudo mv geckodriver /usr/local/bin/

### Enable Headless Mode
edit /scraper/engine/browser.py and set headless to True

## Error
```
Traceback (most recent call last):
  File "/home/user/domain-scraper/env/lib/python3.11/site-packages/anyio/_core/_sockets.py", line 186, in connect_tcp
    addr_obj = ip_address(remote_host)
               ^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.11/ipaddress.py", line 54, in ip_address
    raise ValueError(f'{address!r} does not appear to be an IPv4 or IPv6 address')
ValueError: 'registry.scamscan.net' does not appear to be an IPv4 or IPv6 address
```
set your current ip in the .env file

## Run docker
`docker run -d -t --name scraper -e NODEID='your_node_ip' scraper_{aarch64 or x64}`