#!/usr/bin/python

import csv

def decorate(x):
    if x[1]:
        return "<b>" + x[0] + "</b>"
    else:
        return x[0]

with open('picksix.csv', 'r') as csvfile:
    reader = csv.reader(csvfile)
    teams = next(reader)
    markers = next(reader)

    for row in reader:
        poster = row[0]
        try:
            score = int(row[1])
        except (TypeError, ValueError):
            continue

        zipped = zip(teams, markers, row)
        filtered = filter(lambda x: bool(x[0] and x[2]), zipped)
        myteams = map(decorate, filtered)

        print("<b>{0}</b> - {1} ({2})".format(poster, score, ", ".join(myteams)))

