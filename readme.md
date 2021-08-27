# Stop the process of hanging scraping jobs


## Description
The Python script for killing the hanged scrapy processes.


## Setup and deployment
- `git clone https://github.com/mtrineyev/calm-life.git`
- `cd calm-life`
- `cp config.ini.example config.ini`
- `nano config.ini` and set the variables as described in the comments
- `sudo apt-get install python3-dev`
- `sudo apt-get install python3-venv`
- `python3 -m venv venv`
- `source venv/bin/activate`
- `pip install -r requirements.txt`
- `nano calm-life.sh` and copy the code below
```
        #!/bin/bash
        cd /home/USER/calm-life
        source venv/bin/activate
        python main.py
        deactivate
```
- `chmod +x calm-life.sh`


## To test the script
`cd /home/USER/calm-life`, run `calm-life.sh` then run the `seen_processes.py` script to see list of the seen processes.


## The licence
The script is free software written by Maksym Trineyev (mtrineyev@gmail.com).

It comes with ABSOLUTELY NO WARRANTY, to the extent permitted by applicable law.
