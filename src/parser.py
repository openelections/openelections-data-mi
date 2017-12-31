#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

# The MIT License (MIT)
# Copyright (c) 2017 OpenElections
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all 
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
# SOFTWARE.

import csv
import os
from enum import Enum, auto
import argparse
import pandas
import collections

def main():
    args = parseArguments()

    parser = MIParser(args.stateDirPath, args.date, args.outDirPath)
    parser.writeOut()

def parseArguments():
    parser = argparse.ArgumentParser(description='Parse Michigan SOS CSV files into OpenElections format')
    parser.add_argument('stateDirPath', metavar='MI_dir_path', type=str,
                        help='path to the directory with the Michigan CSV files for a given year')
    parser.add_argument('date', type=str,
                        help='the date of the election(s) in YYYYMMDD format')
    parser.add_argument('outDirPath', type=str,
                        help='path to output the CSV file(s) to')


    return parser.parse_args()

class MIParser(object):
    OFFICE_CODES = {
        1: "President",
        2: "Governor",
        3: "Secretary of State",
        4: "Attorney General",
        5: "U.S. Senate",
        6: "U.S. House",
        7: "State Senate",
        8: "State House"
    }


    def __init__(self, stateDirPath, date, outDirPath):
        self.stateDirPath = stateDirPath
        self.date = date
        self.year = date[0:4]
        self.state = 'mi'
        self.outDirPath = outDirPath
        self.merged = None
        self.results = collections.defaultdict(list)

        self.buildFileTable()
        self.readIn()
        self.process()

    
    def readIn(self):
        def table(file):
            options = { 'header': None,                 # Data has no header row
                        'index_col': False,             # Data has no index column; let pandas assign PK itself
                        'na_filter': False,             # Load empty cells as empty string, not NaN
                        'dtype': {'district': object}}  # Treat 'district' as a string, not a number

            return pandas.read_table(self.files[file]['path'], **options, names=self.files[file]['cols'])

        # read and merge tables, LEFT JOINing on key columns
        df1 = pandas.merge(table('city'), table('county'), on='countyCode')
        df2 = pandas.merge(df1, table('vote'), on=['year', 'type', 'countyCode', 'cityCode'])
        df3 = pandas.merge(df2, table('name'), on=['year', 'type', 'officeCode', 'district', 'status', 'candidateID'])

        # Sort into sensible order
        self.merged = df3.sort_values(['countyName', 'cityCode', 'precinct', 'officeCode', 'district'])

    
    def process(self):
        for index, row in self.merged.iterrows():
            if row['officeCode'] in MIParser.OFFICE_CODES:
                precinct = row['precinct']

                if precinct != 9999:
                    precinct = f"{row['cityName'].title()} {row['precinct']}"

                    label = row['precinctLabel'].strip()
                    if label:
                        if label == 'AVCB':
                            precinct += " "

                        precinct += f"{label}"

                    if row['ward']:
                        precinct += f" Ward {row['ward']}"
                
                office = MIParser.OFFICE_CODES[row['officeCode']]
                district = row['district'][0:3]
                party = row['party'].strip()
                candidate = ' '.join(filter(None, [row['first'], row['middle'], row['last']])).strip().title() # exclude empty strings
                
                if district == '000':
                    district = None
                else:
                    district = int(district)

                electionType = None
                if row['status'] == 0:
                    electionType = 'general'
                elif row['status'] == 8:
                    electionType = 'special'
                
                if not electionType:
                    print(f"ERROR: Unknown status for vote: {row}")
                else:
                    result = [row['countyName'].title(), precinct, office, district, party, candidate, row['votes']]
                    self.results[electionType].append(result)
        

    def buildFileTable(self):
        self.files = {
            'name': {   'path': os.path.join(self.stateDirPath, self.year+"name.txt"),
                        'cols': ['year', 'type', 'officeCode', 'district', 'status', 'candidateID', 'last', 'first', 'middle', 'party']},
            'county': { 'path': os.path.join(self.stateDirPath, "county.txt"),
                        'cols': ['countyCode', 'countyName']},
            'vote': {   'path': os.path.join(self.stateDirPath, self.year+"vote.txt"),
                        'cols': ['year', 'type', 'officeCode', 'district', 'status', 'candidateID', 'countyCode', 'cityCode', 'ward', 'precinct', 'precinctLabel', 'votes']},
            'city': {   'path': os.path.join(self.stateDirPath, self.year+"city.txt"),
                        'cols': ['year', 'type', 'countyCode', 'cityCode', 'cityName']}
        }

    
    def writeOut(self):
        for electionType, results in self.results.items():
            path = os.path.join(self.outDirPath, f"{self.date}__{self.state}__{electionType}__precinct.csv")
            self.writeResultsToFile(path, results)

    def writeResultsToFile(self, outDirPath, results):
        with open(outDirPath, 'w') as outfile:
            writer = csv.writer(outfile, lineterminator='\n')
            writer.writerow(['county', 'precinct', 'office', 'district', 'party', 'candidate', 'votes'])
            writer.writerows(results)


# Default function is main()
if __name__ == '__main__':
    main()
