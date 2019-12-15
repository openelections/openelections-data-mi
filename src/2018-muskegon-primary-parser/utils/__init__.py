"""
This python script contains commonly used functions to help with parsing in the openelections project.
Original Author: Tiffany Xiao
Edited By: Karen Santamaria
Date: 11/19/2019
"""

import csv


def standardize_office_name(office_to_check):
    ''' 
    Function to change office name into the standard office name as requested 
    https://github.com/openelections/docs/blob/master/standardization.md
    
    Sample Input: 'United States Representative District 8'
    Sample Output: U.S. House
    '''

    formatted_office = None 

    not_accepted_offices = ["city"]
    office_to_check = office_to_check.lower().strip()

    lieutenant_governor_list = ["lt.","lieutenant", "lt governor"]
    governor_list = ["governor"]
    attorney_general_list = ["attorney general"]
    us_senate_list = ["us senator", "united states senator", "us senate"]
    state_senate_list = ["state senate", "state senator"]
    state_assembly_list = ["state assembly", "member of the state assembly", "assembly"]
    secretary_of_state_list = ["secretary of state"]
    controller_list = ["controller"]
    state_treasurer_list = ["treasurer of state"]
    insurance_commissionar_list = ["insurance commissioner"]
    public_instruction_list = ["public instruction"]
    us_house_list = ["us house",
                        "u.s. house",
                        "united state house",
                        "us rep",
                        "u s rep",
                        "u.s. rep",
                        "united states rep", 
                        "representative in congress"]
    state_house_list = ["representative in state legislature",
                         "state representative"]
    auditor_of_state_list = ['auditor of state']


    office_names_master = {
        'Lieutenant Governor' : lieutenant_governor_list,
        'Governor' : governor_list,
        'Attorney General' : attorney_general_list,
        'U.S. Senate' : us_senate_list,
        'State Senate' : state_senate_list,
        'State Assembly' : state_assembly_list,
        'State Secretary' : secretary_of_state_list,
        'Controller' : controller_list,
        'State Treasurer' : state_treasurer_list,
        'Insurance Commisioner' : insurance_commissionar_list,
        'Public Instruction' : public_instruction_list,
        'U.S. House' : us_house_list,
        'State House' : state_house_list,
        'State Auditor' : auditor_of_state_list
    }

    # for each office check if any are a match
    for key in office_names_master:
        if(is_this_office(office_names_master[key], key, office_to_check)):
            formatted_office = key # if match change to desired office format
            break

    return formatted_office



def is_this_office(accepted_office_lst, office_name, office_to_check):
    '''
    Find if office_to_check is a match to given office_name
    SAMPLE INPUT:
        accepted_office_lst = ["us senator", "united states senator", "us senate"]
        office_name = U.S. Senator
        office_to_check = United States Senator
    SAMPLE OUTPUT: True 
    '''
    is_this_office_type = False

    offices_with_us = ['U.S. Senate', 'U.S. House'] # offices that require US explicitly stated
    offices_with_lt = ['Lieutenant Governor'] # offices that require Lt. explicitly stted

    us_in_name = True if (office_name in offices_with_us) else False #check is US has to be in office name
    lt_in_name = True if (office_name in offices_with_lt) else False #check if Lt. has to be in office name

    us_names = ['u.s.', 'us', 'united state', 'congress'] # ways US is writted
    lt_names = ['lt', 'lieutenant' ] # ways Lt. is written

    for office in accepted_office_lst:
        if (us_in_name): 
            if(office in office_to_check):
                for us_name in us_names:
                    if (us_name in office_to_check):
                        is_this_office_type = True
        elif (lt_in_name):
            if(office in office_to_check):
                for lt_name in lt_names:
                    if (lt_name in office_to_check):
                        is_this_office_type = True
        else:
            if (office in office_to_check):
                is_this_office_type = True


    return is_this_office_type