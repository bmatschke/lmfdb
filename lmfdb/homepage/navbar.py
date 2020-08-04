# -*- coding: utf-8 -*-

import os
import yaml
from flask import url_for
from copy import deepcopy

# The unique instance of the class NavBar:

the_navbar = None

# Function to create the unique NavBar instance if necessary, and return it:

def get_navbar():
    global the_navbar
    if the_navbar is None:
        the_navbar = NavBar()
    return the_navbar

# The NavBar class, created by parsing the file navbar.yaml

class NavBar(object):
    """
    Class for holding the navbar content.
    """
    def __init__(self):
        _curdir = os.path.dirname(os.path.abspath(__file__))
        self.toc_dic = yaml.load(open(os.path.join(_curdir, "navbar.yaml")), Loader=yaml.FullLoader)
        
        print("self.toc_dic:",self.toc_dic)
        
        self.main_headings = list(self.toc_dic)
        self.main_headings.sort()
 
        #heading = lambda k: linked_name(self.toc_dic[k]['heading'],'heading')
        #self.data = [(k,heading(k),self.toc_dic[k]) for k in self.main_headings]

        
        def add_helpers_to_dropdown_dict(item):
            # Add some (redundant) entries into the dropdown dictionary `item` (or one of its items),
            # which make it easier to read by the template.
            
            #print("item:",item) #debug
         
            item['only_in_beta'] = 'status' in item and item['status'] == 'beta'
            item['requires_auth_or_beta'] = 'requires' in item and item['requires'] == "auth_or_beta"
            item['requires_not_beta'] = 'requires' in item and item['requires'] == "not_beta"
            item['is_link'] = 'url_for' in item
            if item['is_link']:
                item['url'] = url_for(item['url_for'],**item.get('url_args',dict()))
            item['is_link_bar'] = 'type' in item and item['type'] == 'link_bar'
            
            recurse_keys = ['groups','parts','entries']
            for key in recurse_keys:
                if key in item:
                    for part in item[key]:
                        add_helpers_to_dropdown_dict(part)
            if 'heading' in item:
                add_helpers_to_dropdown_dict(item['heading'])
            
            return        

        self.dropdowns = []
      
        for main_heading in self.main_headings:
            parsed_dropdown = self.toc_dic[main_heading]
            
            #Unify the dropdown menu's syntax for easier parsing by template:
            if 'groups' in parsed_dropdown:
                dropdown = deepcopy(parsed_dropdown)
            elif 'parts' in parsed_dropdown:
                #wrap parsed_dropdown's parts into a single group of menu items:
                dropdown = {prop: deepcopy(parsed_dropdown[prop]) for prop in parsed_dropdown if prop not in 'parts'}
                group = {'title': "", 'parts': deepcopy(parsed_dropdown['parts'])}
                dropdown['groups'] = [group]
            else:
                dropdown = deepcopy(parsed_dropdown)
                
            add_helpers_to_dropdown_dict(dropdown)
            
            self.dropdowns.append(dropdown)
                
            
            print("main_heading:",main_heading)
            print("dropdown:",dropdown)
            
            
