import csv

OFFICE_CODES = {
    "1": "President",
    "2": "Governor",
    "3": "Secretary of State",
    "4": "Attorney General",
    "5": "U.S. Senate",
    "6": "U.S. House",
    "7": "State Senate",
    "8": "State House"
}

with open("/Users/dwillis/code/openelections-sources-mi/2016/2016name.txt", 'rb') as csvfile:
    names = []
    reader = csv.reader(csvfile, delimiter='\t')
    for row in reader:
        names.append(row)
    names = [n for n in names if int(n[2]) < 9]

with open("/Users/dwillis/code/openelections-sources-mi/2016/county.txt", 'rb') as countyfile:
    counties = []
    reader = csv.reader(countyfile, delimiter='\t')
    for row in reader:
        counties.append(row)

with open("/Users/dwillis/code/openelections-sources-mi/2016/2016vote.txt", 'rb') as votefile:
    results = []
    votesfile = csv.reader(votefile, delimiter='\t')
    for row in votesfile:
        if int(row[2]) < 9 and int(row[2]) > 0:
            name = [n for n in names if row[5] == n[5]][0]
            county = [c for c in counties if row[6] == c[0]][0]
            office = OFFICE_CODES[row[2]]
            candidate = name[7] + ' ' + name[8]+ ' ' + name[6]
            candidate = candidate.replace("  "," ")
            district = row[3][0:3]
            if district == '000':
                district = None
            results.append([county[1], row[10], office, district, name[9], candidate, row[11]])

with open("20161108__mi__general__precinct.csv", 'wb') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(['county', 'precinct', 'office', 'district', 'party', 'candidate', 'votes'])
    writer.writerows(results)
