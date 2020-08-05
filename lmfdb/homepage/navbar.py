# -*- coding: utf-8 -*-

import os
import yaml
from flask import url_for
from copy import deepcopy
from sage.all import cached_function

# The unique global instance of the class NavBar:

the_navbar = None


def get_navbar():
    """
    Function to create the unique NavBar instance if necessary, and return it:
    """
    global the_navbar
    if the_navbar is None:
        the_navbar = NavBar()
    return the_navbar


class NavBar(object):
    """
    Class for holding the navbar content.
    Created by parsing the file navbar.yaml.
    """
    def __init__(self):
        _curdir = os.path.dirname(os.path.abspath(__file__))
        self.toc_dic = yaml.load(open(os.path.join(_curdir, "navbar.yaml")), Loader=yaml.FullLoader)
        
        print("self.toc_dic:",self.toc_dic)
        
        self.main_headings = list(self.toc_dic)
        self.main_headings.sort()
 
        #heading = lambda k: linked_name(self.toc_dic[k]['heading'],'heading')
        #self.data = [(k,heading(k),self.toc_dic[k]) for k in self.main_headings]

        
        def add_helpers_to_dropdown_dict(item,parent_status="",family_css=""):
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
            
            
            #Inherit status, if none prescribed:
            if 'status' not in item:
                item['status'] = parent_status
            
            #CSS-classes:
            if 'css_classes' not in item:
                item['css_classes'] = ""
            item['css_classes'] += " " + item['status']
            item['css_classes'] += " " + family_css
            #clean the css string:
            print("item['css_classes']:",item['css_classes'])
            print(item['css_classes'].split(' '))
            print(set(item['css_classes'].split(' ')))
            print(set(item['css_classes'].split(' ')).difference([' ']))
            item['css_classes'] = " ".join(set(item['css_classes'].split(' ')).difference([' ']))
                
            recurse_keys = ['groups','parts','entries']
            for key in recurse_keys:
                if key in item:
                    for part in item[key]:
                        css = part['css_classes'] if 'css_classes' in part else ''
                        add_helpers_to_dropdown_dict(part, item['status'], css)
            if 'heading' in item:
                add_helpers_to_dropdown_dict(item['heading'], item['status'])
            
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

        def item_is_constaint(item,is_beta,is_auth):
            
            if 'status' in item:
                if item['status'] == 'beta' and not is_beta:
                    return True
                if item['status'] == 'future' and not is_beta:
                    return True
            
            if 'requires' in item:
                if item['requires'] == 'auth' and not is_auth:
                    return True
                if item['requires'] == 'not_auth' and is_auth:
                    return True
                if item['requires'] == 'beta' and not is_beta:
                    return True
                if item['requires'] == 'not_beta' and is_beta:
                    return True
                if item['requires'] == 'auth_or_beta' and not (is_auth or is_beta):
                    return True
                if item['requires'] == 'auth_and_beta' and not (is_auth and is_beta):
                    return True
                    
            return False        
                
            
        def get_constraint_dropdowns(item,is_beta,is_auth):    
            
            if isinstance(item,list):
                constaint_elements = [get_constraint_dropdowns(element,is_beta,is_auth) for element in item]
                result = [element for element in constaint_elements if element != None]
                return result
            
            elif isinstance(item,dict):
                if item_is_constaint(item,is_beta,is_auth):
                    return None
                result = {item: get_constraint_dropdowns(value,is_beta,is_auth) for item,value in item.items()}
                return result
            else:
                return item
    
        self.dropdowns_constraint = {}
        for is_beta in [True,False]:
            for is_auth in [True,False]:
                self.dropdowns_constraint[is_beta,is_auth] = get_constraint_dropdowns(self.dropdowns,is_beta,is_auth)
                print("is_beta,is_auth:",is_beta,is_auth)
                print("dropdowns_constraint[is_beta,is_auth]:",self.dropdowns_constraint[is_beta,is_auth])
 
