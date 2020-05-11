#!/usr/bin/env python

'''
Example custom dynamic inventory script for Ansible, in Python.
'''

import os
import sys
import argparse
import csv

try:
    import json
except ImportError:
    import simplejson as json



class ExampleInventory(object):

    def __init__(self,inventory_file):
        self.inventory_file = inventory_file
        self.inventory = {}
        self.read_cli_args()

        # Called with `--list`.
        if self.args.list:
            self.inventory = self.read_csv_file(self.inventory_file)
        # Called with `--host [hostname]`.
        elif self.args.host:
            # Not implemented, since we return _meta info `--list`.
            self.inventory = self.empty_inventory()
        # If no groups or vars are present, return an empty inventory.
        else:
            self.inventory = self.empty_inventory()

        print (json.dumps(self.inventory,indent=4));

    # Read the command line args passed to the script.
    def read_cli_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--list', action = 'store_true')
        parser.add_argument('--host', action = 'store')
        self.args = parser.parse_args()

    def read_csv_file(self,inventory_file):
        
        #Initialize a dict
        inventory_data = {}
        #Read the CSV and add it to the dictionary
        with open(inventory_file, 'r') as fh:
            csvdict = csv.DictReader(fh)
            for rows in csvdict:
                #import pdb;pdb.set_trace()
                hostname = rows['Device Name']
                inventory_data[hostname] = rows

        result = self._build_ansible_data(inventory_data)
        return result
        #return inventory_data

    def _build_ansible_data(self,csv_inventory_data):
        
        #print(json.dumps(csv_inventory_data))

        all_platforms = set([i['Platform'] for i in csv_inventory_data.values() ])
        all_locations = set([i['Location'] for i in csv_inventory_data.values() ])
        
        ansible_grps = dict()

        for p in all_platforms:
            
            hosts = [ i['Device Name'] for i in csv_inventory_data.values() if i['Platform'] == p ]

            ansible_grps[p] = {'hosts':hosts}

        for l in all_locations:
            
            hosts = [ i['Device Name'] for i in csv_inventory_data.values() if i['Location'] == l ]

            ansible_grps[p] = {'hosts':hosts}
        
        ansible_grps['all'] = list(csv_inventory_data.keys())

        ansible_meta = dict()

        sub_dict = {}
        
        ansible_meta['_meta'] = {'hostvars': sub_dict }

        for h in csv_inventory_data:
            host_vars = {}
            host_vars['ansible_host'] = csv_inventory_data[h]['Mgmt IP']
            host_vars['ansible_network_os'] = csv_inventory_data[h]['Platform']
            sub_dict[h] = host_vars

        return { **ansible_grps ,**ansible_meta}


    # Empty inventory for testing.
    def empty_inventory(self):
        return {'_meta': {'hostvars': {}}}


if __name__ == "__main__" :
    inventory_file = "myinventory.csv"
    ExampleInventory(inventory_file=inventory_file)
    #myinventory = get_structured_inventory(inventory_file)
    #print(json.dumps(myinventory, indent=4))