# on-the-record
NDNation On The Record basketball prediction contest

## Requirements
Running the scripts for the prediction contest requires the following:
* Python 3.x
* [Pystache](https://pypi.org/project/pystache/)

## Working With the Game Database
The database for the current season is found under the `data/hoops` directory (a symlink to the
actual season directory). All command examples below assume that to be your current working
directory, and that directory has symlinks to the necessary scripts and templates in the root
directory.

The list of games and their IDs and scores can be viewed by running the `hoops.py` script:
```
$ python3 hoops.py
1 Radford 79 76
2 Youngstown St. 88 81
3 Southern Indiana None None
...
30 Pittsburgh None None
31 at Clemson None None
```

## Contest Update Process
### Import Predictions and Game Scores
On The Pit, copy and paste the prediction thread -- the whole thing -- from the message board page
(not from the thread itself) into a text editor.

Insert a new first line into the text file of the format: `@@ {Game ID} {ND score} {Opp. score} @@`
For example:
```
@@ 1 79 76 @@
Everybody on the record for Radford - El Kabong  2022-11-06 12:42:18  [Tag Thread]  [Show All]
78 62 * - NDLuthy  2022-11-10 19:11:18
ND 72 Radford 65 * - bobnd80  2022-11-10 18:14:32
Irish 76 - Highlanders 63 * - IZZYV  2022-11-10 18:11:15
```

Run the `predictions.py` script on the text file with the picks:
```
$ python3 predictions.py rad.txt
```

Alternatively, you can omit the first line from the text file and supply the scores to the script
directly:
```
$ python3 predictions.py rad.txt 1 79 76
```

### Generate the Contest Pages
Once the picks and scores are imported, regenerate the main page, game pages, and contest
leaderboards by running the `leaderboard.py` script:
```
$ python3 leaderboard.py
```
This script will regenerate a fresh copy of all files so as to pick up any corrections that may
have been made in the database.

### Upload the Pages to NDNation
The `upload.py` script will upload all of the HTML files for the content to the appropriate
directory on NDNation's server:
```
$ python3 upload.py
Password: 
Uploading game01.html
Uploading index.html
Uploading scoring.html
Uploading game02.html
```

## Contributing
If you would like to contribute picks or other updates to the contest, please reach out to me by
email (find a link on the contest page at NDNation) or fork this repo and create a pull request.
