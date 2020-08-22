# colorado-tag-check

Host script on Amazon EC2 instance.

Install the following pip modules:
pandas
pdfminer3
requests

Create crontab:
# Runs script every 5 min
*/5 * * * * /.../main.py

# reboots the system once a day at 0300
00 3 * * * sudo reboot
