# colorado-tag-check

- Host script on Amazon EC2 instance.
- Install the following pip modules:
 - pandas
 - pdfminer3
 - requests

**Create Cron Job**

> crontab -e

Pulls from Repo every 2 min
> */2 * * * * cd /home/directory/colorado-tag-check && git pull

Runs script every 5 min
> */5 * * * * cd /home/directory/colorado-tag-check && python main.py

Reboots the system once a day at 0300
> 00 3 * * * sudo reboot
