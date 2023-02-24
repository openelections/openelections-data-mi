import csv
from itertools import zip_longest
import requests
from bs4 import BeautifulSoup

def grouper(iterable, n, *, incomplete='fill', fillvalue=None):
    "Collect data into non-overlapping fixed-length chunks or blocks"
    args = [iter(iterable)] * n
    if incomplete == 'fill':
        return zip_longest(*args, fillvalue=fillvalue)
    if incomplete == 'strict':
        return zip(*args, strict=True)
    if incomplete == 'ignore':
        return zip(*args)
    else:
        raise ValueError('Expected fill, strict, or ignore')

office = "State House"

districts = { 10: '17', 11: "18", 12: "19", 13: "20", 14: "21", 57: "22", 58: "23", 59: "24", 60: "25", 61: "26", 62: "27", 63: "28", 65: "29", 66: "30"}

results = []

for d in districts.keys():

    url = f"https://electionresults.macombgov.org/m37/{districts[d]}-bd-print.html"
    district = d

    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    table = soup.find('table', class_="totalstable")

    # find candidates

    candidates_with_party = [[x.find('b').text, x.find('font').text] for x in table.find_all('tr')[0].find_all('th')[3:-1]]


    for row in table.find_all('tr')[2:]:
        print(row)
        if row.find('td') and row.find('td')['class'][0] == "precinctname":
            precinct_base = row.find('td').text
        elif row.find('td') and row.find('td')['class'][0] == "outsideborder":
            try:
                precinct_num = row.find_all('td')[1].text
                if precinct_num:
                    precinct = precinct_base + " " + precinct_num
                    ballots_cast = row.find_all('td')[2].text.replace(',','')
                    results.append(['Macomb', precinct, office, district, "Ballots Cast", None, None, None, ballots_cast])
                    vote_groups = list(grouper([x.text.replace(',','') for x in row.find_all('td')[3:-1]], 3))
                    for idx, cp in enumerate(candidates_with_party):
                        vote_group = vote_groups[idx]
                        results.append(['Macomb', precinct, office, district, cp[0], cp[1].replace(')','').replace('(',''), vote_group[0], vote_group[1], vote_group[2]])
            except:
                continue
        else:
            continue

with open("macomb_state_house.csv", 'w') as output_file:
    writer = csv.writer(output_file)
    writer.writerow(['county', 'precinct', 'office', 'district', 'candidate', 'party', 'absentee', 'election_day', 'votes'])
    writer.writerows(results)
