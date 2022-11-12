#!/usr/bin/python3

from ftplib import FTP
from getpass import getpass
import sys

ftp = FTP('ndn.hdxen.com')
password = getpass()
ftp.login('irishmace@ndnation.com', password)
ftp.cwd(sys.argv[1])

for filename in ftp.nlst():
    if filename[0] == '.':
        continue
    with open(filename, 'w') as outfile:
        print('Downloading ' + filename)
        ftp.retrlines('RETR ' + filename, lambda line: print(line, file=outfile))

ftp.quit()
