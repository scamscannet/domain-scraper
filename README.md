# domain-scraper
 
## Installtion
* Copy the env.example to .env and edit the env variables:

  * API="https://api.scamscan.net"
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
`docker login ghcr.io -u github_username -p access_token`
`docker run -d -t --name scraper -e NODEID='your_node_id' --dns 8.8.8.8 --dns 8.8.4.4 --restart unless-stopped ghcr.io/scamscannet/domain-scraper:main`

## Development
A static mock of the API (`tests/mock_api.py`) always hands out an example.com job and accepts the uploads.
* `pip install -r requirements-dev.txt`
* `litestar --app tests.mock_api:app run --reload --port 8000`
* set `API="http://127.0.0.1:8000"` in your .env and start the scraper
* `pytest tests/test_scrape_example.py` runs a full job against the mock API (it starts the mock itself)

## Todo
* move to enthec/webappanalyzer
