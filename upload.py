#!/usr/bin/python3

import glob
from ftplib import FTP
from getpass import getpass

ftp = FTP('ndn.hdxen.com')
password = getpass()
ftp.login('irishmace@ndnation.com', password)
ftp.cwd('hoops')

for filename in glob.iglob('*.html'):
    with open(filename, 'rb') as file:
        print('Uploading ' + filename)
        ftp.storlines('STOR ' + filename, file)

ftp.quit()
