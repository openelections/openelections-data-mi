import csv
import requests
from bs4 import BeautifulSoup

base_url = "https://electionresults.ewashtenaw.org/electionreporting/nov2022/canvassreport"

offices = {
    '1': ('Straight Party', None),
    '2': ('Governor', None),
    '3': ('Secretary of State', None),
    '4': ('Attorney General', None),
    '5': ('U.S. House', 6),
    '6': ('State Senate', 14),
    '7': ('State Senate', 15),
    '8': ('State House', 23),
    '9': ('State House', 31),
    '10': ('State House', 32),
    '11': ('State House', 33),
    '12': ('State House', 46),
    '13': ('State House', 47),
    '14': ('State House', 48)
}

results = []

for o in offices.keys():
    office, district = offices[o]
    url = base_url + o + ".html"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find_all('table')[1]
    candidates_with_party = [x.text.split('(') for x in table.find_all('th')][1:]
    precincts = [x.find('td').text.strip() for x in table.find_all('tr')[1:-1]]
    rows = table.find_all('tr')[1:-1]
    for num, row in enumerate(rows):
        votes = [x.text.replace("\xa0","") for x in row.find_all('td')][1:]
        for i, val in enumerate(candidates_with_party):
            d = {'office': office, 'district': district, 'precinct': precincts[num]}
            if len(val) == 1:
                d['party'] = None
                d['candidate'] = val[0]
            else:
                d['candidate'] = val[0]
                d['party'] = val[1].replace(')','')
            d['votes'] = votes[i]
            d['county'] = 'Washtenaw'
            results.append(d)
            d = {}

with open("20221108__mi__general__washtenaw__precinct.csv", 'w') as f:
    csvfile = csv.writer(f)
    csvfile.writerow(['county', 'precinct', 'office', 'district', 'candidate', 'party', 'votes'])
    for result in results:
        csvfile.writerow([result['county'], result['precinct'], result['office'], result['district'], result['candidate'], result['party'], result['votes']])
