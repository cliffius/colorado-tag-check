# colorado-tag-check

- Host script on Amazon EC2 instance.
- Install the following pip modules:
 - pandas
 - pdfminer3
 - requests

**Create Cron Job**

> crontab -e

Pulls from Repo every 5 min
> */5 * * * * cd /home/directory/colorado-tag-check && git pull

Runs script every 1 min
> */1 * * * * cd /home/ubuntu/colorado-tag-check && python3 main.py

Reboots the system once a day at 0300
> 00 3 * * * sudo reboot
