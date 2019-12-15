''' 
Description: Parse out election data for Muskegon, MI pdf's
Author: Karen Santamaria   
'''


import csv
import pdftotext
from table import Table, Row
from utils import standardize_office_name
import re
import os
from os import listdir
from os.path import isfile, join


def is_int(s):
    '''check if a value is an integer'''
    try: 
        int(s)
        return True
    except ValueError:
        return False

def is_candidate_row(line):
    '''check if line is a candidate row with candidate name and votes'''
    return (len(line) >= 8
            and is_int(line[-2])
            and ['Cast', 'Votes:'] != line[0:2])
    
def is_office_name(line):
    '''check if the next line is an office name'''
    return ('Party -' in list_to_string(line))

def is_precinct_name(line):
    '''check if line contains precinct name'''
    
    return ('precinct' in list_to_string(line).lower()
            and is_int(line[-1]))

def is_county_name(line):
    '''check if line contains county name'''
    return ('County,' in line)

def list_to_string(line):
    '''change list to string'''
    return ' '.join(line)

def create_row(office, district, precinct, county, party, candidate_line):
    '''create row object'''
    absent = candidate_line[-6]
    election_day = candidate_line[-4]
    total_vote = candidate_line[-2]
    candidate = get_candidate(candidate_line)
    row = Row(county, precinct, office, district, party, candidate, total_vote, election_day=election_day, absentee=absent)
    return row

def get_no_letter(strng):
    return re.sub(r'[^0-9]+', '', strng)
    
def get_district(office_lst):
    '''
    extract district number if present
    VOTES= 452 State Representative District 17 -> 17
    '''
    district = ''
    for i in range(1, len(office_lst)-1):
        if('dist' in office_lst[i].lower()):
            if(is_int(get_no_letter(office_lst[i+1]))): 
                # if district number after office name
                district = get_no_letter(office_lst[i+1])
            elif(is_int(get_no_letter(office_lst[i-1]))):
                # if district number before office name
                district = get_no_letter(office_lst[i-1])      
    return district

def get_party(office_party_line):
    '''
    get party from a candidate line
    ['16', '10', '0', '26', '7.22%', '(L)', 'Lucy', 'M', 'Brenton'] -> L
    '''
    party = list_to_string(office_party_line).split('-')[1].lower()
    
    if('republican party' in party):
        party = 'R'
    elif('democratic party' in party):
        party = 'D'
    elif('libertarian party' in party):
        party = 'L'

    return party
    
    
def get_candidate(candidate_line):
    '''get name from a candidate line
    ['16', '10', '0', '26', '7.22%', '(L)', 'JANE', 'M', 'DOE'] -> Jane M Doe
    '''
    candidate =  list_to_string(candidate_line[0:-6])
    
    return candidate

def get_precinct(precinct_line):
    '''get precinct name formatted'''
    precinct = precinct_line
    for i in range(0, len(precinct)):
        precinct[i] = precinct[i].capitalize()
    
    precinct = list_to_string(precinct)
    precinct = precinct.replace('Name:', '' )
    precinct = precinct.replace('Precinct', '' )
    precinct = " ".join(precinct.split())
    
    return precinct

def import_pdf(filename):
    '''import pdf and get a list that contains all the lines in list format'''
    with open(filename, "rb") as f:
        pdf = pdftotext.PDF(f)
        
    formatted_lines = []
    for page in pdf:
        lines = page.split('\n')
        for i in range(0, len(lines)):
            lines[i] = lines[i].replace('•', '')
            line_lst = ' '.join(lines[i].split()).split(' ')
            formatted_lines.append(line_lst)
    

    return formatted_lines

def get_office(line):
    '''
    get string line and output office
    '''
    office = list_to_string(line).strip().lower()
    
    if('=' in office):
        office = office.replace('VOTES', '')
        office = office.replace('=', '')
        office = office.strip()
    if(is_int(office.split(' ')[0])):
        office = list_to_string(office.split(' ')[1:])
    
    office = (standardize_office_name(office))
    
    return office
    
           
def create_table(formatted_lines):
    '''create table to make csv'''

    cur_office = ''
    cur_precinct = ''
    cur_county = get_county_name(formatted_lines)
    cur_district = ''
    cur_party = ''
    table = Table()
    
    
    for i in range(0, len(formatted_lines)):
        cur_line = formatted_lines[i]
        if(is_candidate_row(cur_line) and cur_office != None and cur_precinct):
            row = create_row(cur_office, cur_district, cur_precinct, cur_county, cur_party, cur_line)
            table.add_to_table(row)
        elif(is_office_name(cur_line)):
            cur_district = get_district(cur_line)
            cur_office = get_office(cur_line)
            cur_party = get_party(cur_line)
        elif(i < len(formatted_lines)-2 and is_precinct_name(cur_line) ):
            cur_precinct = get_precinct(cur_line)

    return table

def get_election_date(formatted_lines):
    date = ''
    date_lst = []
    for i in range (len(formatted_lines)):
        if list_to_string(formatted_lines[i]).startswith("Run Date"):
            date_lst = formatted_lines[i][3].split('/')
    
        if (len(date_lst) == 3):
            
            year = date_lst[2]
            month = date_lst[0]
            day = date_lst[1]
            
            if (len(month) == 1):
                month = '0' + month
            if (len(day) == 1):
                day = '0' + day
        
            date = year + month + day
    
            break
    
    return date

def get_out_filename(formatted_lines):
    '''get filename for csv output'''
    
    date = get_election_date(formatted_lines)
    state = 'mi'
    election_type = 'primary'
    result_type = 'precinct'
    county = get_county_name(formatted_lines).lower()
    
    filename = "__".join([date, state, election_type, county, result_type]) + '.csv'

    return filename

def get_county_name(formatted_lines):
    '''get county name for filename'''
    county = ''
    for cur_line in formatted_lines:
        if (is_county_name(cur_line)):
            return cur_line[0].lower().capitalize()
    return county

def create_csv(in_filepath, out_filepath):
    
    if (in_filepath.endswith('.pdf')):
        imported_pdf = import_pdf(in_filepath)
        table = create_table(imported_pdf)
        csv_filename = get_out_filename(imported_pdf)
        if(len(table.get_rows())):
            table.convert_to_csv(out_filepath + csv_filename)

def main():
    
    in_filepath = input("Enter file or folder to parse: ")
    
    csv_out_dir = input("Enter output directory: ")
    
    csv_out_dir = csv_out_dir if csv_out_dir.endswith('/') else csv_out_dir+'/' 

    
    if not os.path.exists(csv_out_dir):
            os.mkdir(csv_out_dir)
    
    if (in_filepath.endswith('.pdf')):
        create_csv(in_filepath, csv_out_dir)
    else:
        
        pdf_lst = [f for f in listdir(in_filepath) if (isfile(join(in_filepath, f)) and f.endswith('.pdf'))]
        
        for pdf_filename in pdf_lst:
            create_csv(in_filepath, csv_out_dir)
                
                
                
if __name__ == "__main__":
    main()

