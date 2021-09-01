# Stop the process of hanging scraping jobs


## Description
The Python script for killing the hanged scrapy processes.


### Setup and deployment
```bash
$ git clone https://github.com/mtrineyev/calm-life.git
$ cd calm-life
$ cp config_example.yaml config.yaml
$ nano config.yaml  # set the variables as described in the comments
$ sudo apt-get install python3-dev
$ sudo apt-get install python3-venv
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ nano calm-life.sh  # copy the code below without the indents
    #!/bin/bash
    cd /home/USER/calm-life
    source venv/bin/activate
    python main.py
    deactivate
# save the file, exit nano
$ chmod +x calm-life.sh
```

### To test the script
```bash
$ cd /home/USER/calm-life
$ ./calm-life.sh
$ cat ./processes.yaml
```
You should see the list of the seen processes and its count.

### The licence
The script is free software written by [Maksym Trineyev](mailto:mtrineyev@gmail.com).

It comes with ABSOLUTELY NO WARRANTY, to the extent permitted by applicable law.
