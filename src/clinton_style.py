import csv

county = 'Clinton'

lines = open('/Users/derekwillis/code/openelections-sources-mi/2020/general/Clinton MI Precinct Results-11-13-2020 10-46-37 AM_202011130956572086.txt').readlines()
results = []
reg_voters = False

for line in lines:
    if line.strip() == '':
        continue
    if line.strip() == 'Ballots Cast - NONPARTISAN':
        continue
    if line.strip() == 'Ballots Cast - Blank':
        continue
    if line.strip() == 'Voter Turnout - Total':
        continue
    if line[0:14] == 'Contest Totals':
        continue
    if 'Precinct' in line:
        precinct = line.split('\t')[0]
        results.append([county, precinct, 'Registered Voters', None, None, None, None, None, int(line.split('\t')[1].split(' registered voters')[0].split(' of ')[1].replace(',',''))])
        ballot_lines = 0
    elif "Vote for" in line or 'Proposal' in line or "Mid Michigan" in line or "Ballot Question" in line:
        office = line.strip().split(' - ')[0]
    elif 'Cast Votes:' in line:
        if ballot_lines == 0:
            results.append([county, precinct, 'Ballots Cast', None, None, None, int(line.split('\t')[1].replace(',','')), int(line.split('\t')[3].replace(',','')), int(line.split('\t')[5].replace(',',''))])
            ballot_lines = 1
    else:
        if 'Undervotes' in line or 'Overvotes' in line:
            results.append([county, precinct, office, None, party, line.split('\t')[0].replace(':',''), int(line.split('\t')[1].replace(',','')), int(line.split('\t')[3].replace(',','')), int(line.split('\t')[5].replace(',',''))])
        else:
            print(line)
            if '(W)' in line or len(line.split('\t')) == 7:
                candidate = line.split('\t')[0]
                party = None
                results.append([county, precinct, office, None, party, candidate, int(line.split('\t')[1].replace(',','')), int(line.split('\t')[3].replace(',','')), int(line.split('\t')[5].replace(',',''))])
            else:
                # candidate result
                candidate = line.split('\t')[0]
                party = line.split('\t')[1]
                results.append([county, precinct, office, None, party, candidate, int(line.split('\t')[2].replace(',','')), int(line.split('\t')[4].replace(',','')), int(line.split('\t')[6].replace(',',''))])

with open('20201103__mi__general__clinton__precinct.csv', 'wt') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['county', 'precinct', 'office', 'district', 'party', 'candidate', 'absentee', 'election_day', 'votes'])
    writer.writerows(results)
