#!/usr/bin/python

# This class provides relatively efficient calculation of how many rules in working sets
# are reduced by merging together either subjects or objects to support the DomainCreator.

from enum import Enum

TARGET_DELTA = 25

class WorkingSets:
    
    def __init__(self, ws_file, full_pack = False):
        print("Creating a WS object.")
        self.ws_file = ws_file
        self.full_pack = full_pack
        self.raw_sets = self.LoadWorkingSets(self.ws_file)
        print("WS has been initialized.")

    # Reset for a new run with limit ws_limit
    def Reset(self, ws_limit):
        print("Resetting WS object for this run.")
        self.ws_limit = ws_limit - TARGET_DELTA
        # In cases where we periodically readjust target, still want to keep final target around
        self.final_ws_limit = ws_limit - TARGET_DELTA
        self.InitNewRun()

    def SetLimit(self, ws_limit):
        self.ws_limit = ws_limit - TARGET_DELTA

    # Read a WS file, parse into a list of lists
    def LoadWorkingSets(self, ws_file):
        
        print("Loading WS from " + ws_file)
        f = open(ws_file, "r")
        current_set = None
        working_sets = []
        working_set_lengths = []
        read_sets = 0
        is_init = False
        
        # Read out each working set
        for l in f.readlines():
            l = l.strip()
            if "[CU_start.S]" in l:
                is_init=True
            if l == "BEGIN":
                if current_set != None:
                    # Only add WS not from the init setup; we can't compress those
                    if not is_init:
                        working_set_lengths.append(len(current_set))
                        working_sets.append(current_set)
                is_init=False
                current_set = set()
                read_sets += 1
                continue
            current_set.add(l)
            
        # Add the last set too
        if current_set != None and len(current_set) > 0:
            working_sets.append(current_set)

        # If we're doing a full pack, then group them all together into one giant working set
        if self.full_pack:
            all_rules = set()
            for ws in working_sets:
                for rule in ws:
                    all_rules.add(rule)
            working_sets = [list(all_rules)]
            working_set_lengths.append(len(all_rules))

        # Print stats and return
        num_sets = len(working_sets)
        print("We read " + str(read_sets) + " working sets.")

        return working_sets


    # Run through all rules and remove the ws_id from each rule's set. Speeds up future operations.
    def DeleteWS(self, ws_id):

        num_removed = 0
        for rule in self.working_sets:
            if ws_id in self.working_sets[rule]:
                self.working_sets[rule].remove(ws_id)
                num_removed += 1

        print("Deleting WS " + str(ws_id) + ", removed " + str(num_removed))


    def ReportWorkingSetsOver(self):
        working_set_map = {}
        for rule in self.working_sets:
            for ws_id in self.working_sets[rule]:
                if ws_id not in working_set_map:
                    working_set_map[ws_id] = set()
                working_set_map[ws_id].add(rule)
        num_over = 0
        for ws_id in working_set_map:
            rules_in_ws = len(working_set_map[ws_id])
            if rules_in_ws > self.ws_limit:
                num_over += 1
        return num_over

    def ReportRulesOver(self):
        working_set_map = {}
        for rule in self.working_sets:
            for ws_id in self.working_sets[rule]:
                if ws_id not in working_set_map:
                    working_set_map[ws_id] = set()
                working_set_map[ws_id].add(rule)
        rules_over = 0
        for ws_id in working_set_map:
            rules_in_ws = len(working_set_map[ws_id])
            if rules_in_ws > self.ws_limit:
                rules_over += rules_in_ws - self.ws_limit
        return rules_over
    
    # Build a fresh working_sets object from the raw sets
    def InitNewRun(self):

        self.working_sets = {}
        self.ws_lengths = {}
        
        ws_id = 0
        for ws in self.raw_sets:
            
            # Skip working sets that are already satisfied
            if len(ws) < self.ws_limit:
                continue
            
            ws_id += 1
            print("Loaded in WS " + str(ws_id) + " of len " + str(len(ws)))
            self.ws_lengths[ws_id] = len(ws)
            
            for rule in ws:
                
                if rule not in self.working_sets:
                    self.working_sets[rule] = set()

                self.working_sets[rule].add(ws_id)

        '''
        for rule in self.working_sets:
                print(rule)
                print("\t" + str(self.working_sets[rule]))
        '''

    def RecalculateWSLengths(self):
        working_set_map = {}
        for rule in self.working_sets:
            for ws_id in self.working_sets[rule]:
                if ws_id not in working_set_map:
                    working_set_map[ws_id] = set()
                working_set_map[ws_id].add(rule)
                
        for ws in working_set_map:
            length = len(working_set_map[ws])
            self.ws_lengths[ws] = length
            if length < self.final_ws_limit:
                print("\tPruning out " + str(ws))
                self.DeleteWS(ws)
                

    # See if this identifier is present in any of the working sets
    def PresentInWorkingSets(self, identifier):
        for rule in self.working_sets:
            if identifier in rule:
                return True
        return False
        
    # When DomainCreator actually does a merge, we must update our data stores
    def PerformMerge(self, c1, c2):

        affected_rules = []
        for rule in self.working_sets:
            if c2 in rule:
                affected_rules.append(rule)

        deleted_ws = set()
        
        for rule in affected_rules:
            new_rule = rule.replace(c2, c1)

            # Update the list of WSs
            if new_rule not in self.working_sets:
                self.working_sets[new_rule] = self.working_sets[rule]
            else:

                # Update our workign set lengths
                #saved_working_sets = self.working_sets[new_rule].intersection(self.working_sets[rule])
                #for ws in saved_working_sets:
                #    self.ws_lengths[ws] -= 1
                #    if self.ws_lengths[ws] < self.final_ws_limit:
                #        deleted_ws.add(ws)

                # Then set WSs to union
                self.working_sets[new_rule] = self.working_sets[new_rule].union(
                    self.working_sets[rule])
                
            # Then remove affected rule
            del self.working_sets[rule]

        # Removing this, it makes the count off
        #for ws in deleted_ws:
        #    self.DeleteWS(ws)

        self.RecalculateWSLengths()
        
    # How many rules in working sets do we save by merging C1 and C2?
    def CalcSaved_Merge(self, c1, c2):

        # Step 1: figure out which rules are affected by this merge
        # Q: if we are merging c2 into c1, maybe only check c2?
        # Another tip: this could be made fast by storing index into rules by cluster

        # Make a copy of rules affected by this merge, that way we can run the calculations on the copies
        copied_working_sets = {}
        affected_rules = []
        for rule in self.working_sets:
            if c2 in rule:
                affected_rules.append(rule)
            if c1 in rule or c2 in rule:
                # I think safe to not copy, we are not mutating until intersection which makes new
                #copied_working_sets[rule] = self.working_sets[rule].copy()
                copied_working_sets[rule] = self.working_sets[rule]
        if len(affected_rules) == 0:
            return 0

        #print("Merging together " + c1 + " " + c2)
        
        # Step 2: calculate how many WSs are saved
        # This is slightly wrong: guess, does this handle triple+ collisions?
        saved_rules = 0
        for rule in affected_rules:

            #print("\tAffected rule: " + rule)
            
            # Calculate what the new rule looks like
            new_rule = rule.replace(c2, c1)
            #print("\tBecame: " + new_rule)

            # Is this already a rule that we might save with?
            if new_rule not in copied_working_sets:
                copied_working_sets[new_rule] = copied_working_sets[rule]
            else:

                # Figure out which working sets contain both rules
                working_sets_new = copied_working_sets[new_rule]
                #print("\t\tWorking_sets_new: " + str(working_sets_new))
                working_sets_current = copied_working_sets[rule]
                #print("\t\tWorking_sets_current: " + str(working_sets_current))
                working_sets_shared = working_sets_new.intersection(working_sets_current)
                for ws in working_sets_shared:
                    if self.ws_lengths[ws] > self.ws_limit:
                        saved_rules += 1
                    #else:
                    #    raise Exception("WS not over limit?")
                #print("\t\tShared: " + str(len(working_sets_shared)))

                # Add WS into union on new rule
                copied_working_sets[new_rule] = working_sets_new.union(working_sets_current)

            del copied_working_sets[rule]
        
        return saved_rules
