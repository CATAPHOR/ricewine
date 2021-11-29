import re
import sqlite3
import csv
import datetime

#GUI imports
import tkinter

#initialise sqlite interface
con = sqlite3.connect("ricewine.db", detect_types = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
sql = con.cursor()

#class handles/encapsulates card and card-database interactions
class Person:
    def __init__(self):
        self.firstname = ""
        self.surname = ""
        self.university_id = ""
        self.rw_unique_id = -1
        self.expiry_date = []
    
    #read from card to populate data of person
    def read_card(self, input_text):
        #verify validity with regex
        regex_pattern = ("%[a-zA-Z]+,[a-zA-Z]+:[0-9a-zA-Z]*\?" +
                         ";[0-9]+\?" +
                         "\+[0-9]{2}0000[0-9]{2}0000[0-9]{4}\?")
        valid = re.match(regex_pattern, input_text)                 
        
        if valid == None:
            return False
        else:
            input_tracks = valid[0].split("?")
            
            #populate variables with data from tracks
            self.firstname, self.surname = input_tracks[0][1:].split(":")[0].split(",")
            self.university_id = input_tracks[0].split(":")[1]
            self.rw_unique_id = int(input_tracks[1][1:])
            self.expiry_date = list(map(lambda a: int(a), input_tracks[2][1:].split("0000")))
            return True

    #TODO need this? or delete? maybe useful for updating a person...
    #given input, assign attributes of person 
    def assign_attributes(self, firstname, surname, university_id, expiry_date):
        if len(firstname) == 0 or len(surname) == 0:
            return False
        elif (type(expiry_date) != type([]) or len(expiry_date) != 3 or
                not all(isinstance(n, int) for n in expiry_date)):
            return False
        else:
            self.firstname = firstname
            self.surname = surname
            self.university_id = university_id
            self.expiry_date = expiry_date
            return True

    #verification lookup, searches database for customer and updates database accordingly, returns validity
    def lookup(self):
        warning = ""

        #find customer in database
        sql.execute("SELECT * FROM customers WHERE id = ?;", (self.rw_unique_id,))
        dbquery = sql.fetchone()
        #if not valid, end function
        if dbquery == None:
            print("Entry not found! RiceWine ID (card Track #2) does not match records.")
            return "INVALID\n"

        else:
            dbquery = list(dbquery)

            #check whether full name for ricewine id matches database entry
            if dbquery[1] != self.surname or dbquery[2] != self.firstname:
                print("\"" + self.firstname + " " + self.surname +"\" does not match [ ID #" + 
                str(self.rw_unique_id) + ": " + dbquery[2] + " " + dbquery[1] + " ]")
            #check whether university id for ricewine id matches database entry
            elif dbquery[3] != self.university_id:
                print("University ID mismatch: " + self.university_id + " does not match [ ID #" + 
                str(self.rw_unique_id) + ": " + dbquery[3] + " ]")
            else:
                #make expiry date into datetime object
                datetime_expiry_date = datetime.date(self.expiry_date[2], 
                    self.expiry_date[1], self.expiry_date[0])

                #update database's date for entry if card date clearly supercedes
                if dbquery[4] == None or dbquery[4] < datetime_expiry_date:
                    sql.execute("UPDATE customers SET expiry = ? WHERE id = ?;", 
                        (datetime_expiry_date, self.rw_unique_id))
                    con.commit()
                    dbquery[4] = datetime_expiry_date
                    print("Database expiry date updated to match card's date: " + 
                        datetime_expiry_date.isoformat() + ".")

                #if database has a date further ahead than the card it must be outdated and so invalid
                if dbquery[4] > datetime_expiry_date:
                    print("Card expiry date (" + datetime_expiry_date.isoformat() + ") outdated,"
                        + " precedes expiry date on record (" + dbquery[4].isoformat() + ").")
                else:
                    #check if date valid (i.e. after today)
                    if datetime_expiry_date >= datetime.date.today():
                        #increment number of times scanned on database
                        times_used = dbquery[5]
                        sql.execute("UPDATE customers SET times_used = ? WHERE id = ?;", 
                            (times_used + 1, self.rw_unique_id))
                        con.commit()
                        print("Number of times used: " + str(times_used + 1))
                    else:
                        warning = " [WARNING: CARD EXPIRED; RENEW!]"
                    #reaching end of this else block indicates validity; return as such (+ any warning)
                    return "VALID" + warning + "\n"

        #control flow ensures reaching here means card contents invalid in some way
        return "INVALID\n"

    #print attributes (testing)
    def output_attributes(self):
        print("PERSONAL DETAILS")
        print("First name:\t" + self.firstname)
        print("Surname:\t" + self.surname)
        print("University ID:\t" + self.university_id)
        print("Rice Wine ID:\t" + str(self.rw_unique_id))
        print("Expiry Date:\t" + str(self.expiry_date[0]) + "/" +
              str(self.expiry_date[1]) + "/" + str(self.expiry_date[2]))
        print()

def main():
    print("Rice Wine Shop")
    print("Special Offer Card Verification\n")
    
    #MODE SELECTION
    selection = ""
    while selection != "q":
        selection = ""
        print("-" * 10 + "ROOT MENU" + "-" * 10)
        print("Type number to select mode:")
        print("1: Manage database")
        print("2: Verify against database")
        print("3: Write new card")
        print("Q: Quit application")
        selection = input("\n").lower().strip()
        
        #QUIT
        if selection == "q":
            con.close()
            return
        
        #MANAGE DATABASE
        elif selection == "1":
            selection = ""
            while selection != "r":
                selection = ""
                print("-" * 10 + "MANAGING DATABASE" + "-" * 10)
                print("1: View all entries in database")
                print("2: Add to database")
                print("3: Remove from database")
                print("4: Search for and/or edit database entry")
                print("X: Reset database [DANGER]")
                print("R: Return to parent menu")
                selection = input("\n").lower().strip()

                #return to previous menu
                if selection == "r":
                    pass
                #print all database entries
                elif selection == "1":
                    print_table()
                #adds to the table
                elif selection == "2":
                    add_to_table_handler()
                #removes from the table
                elif selection == "3":
                    remove_from_table_handler()
                #find table entry and potentially edit
                elif selection == "4":
                    search_edit_handler()
                #reset database
                #TODO create backup in backup folder
                elif selection == "x":
                    selection = ""
                    while selection not in ["y", "n"]:
                        selection = input("\nAre you sure? This will delete ALL data. Y/N\n").lower()
                    if selection == "y":
                        selection = input("\nEnter admin password: ").lower()
                        if selection == "choomer":
                            new_table()
                        else:
                            print("Password not recognised.\n")
            
        #VERIFY AGAINST DATABASE
        elif selection == "2":
            #TESTING
            test_text = ("%KEN,YANAGIDA:K1892327?" +
                          ";116?" +
                          "+1100001100002022?")
            #%KEN,YANAGIDA:K1892327?;116?+1100001100002022?
            #%KEN,YANAGIDA:K1892327?;116?+1100001100002021?
            #%KEN,YANAGIDA:K1892327?;123456789?+1100001100001999?

            #create object to store card data
            person_to_verify = Person()
            input_text = ""
            print("-" * 10 + "VERIFYING CARDS" + "-" * 10)
            print("Swipe card or type \"QUIT\" to exit verification mode.\n")
            while input_text != "QUIT":
                #get card tracks as one line from stdin
                input_text = input().upper()
                if input_text == "QUIT":
                    pass
                else:
                    if person_to_verify.read_card(input_text):
                        print(person_to_verify.lookup())
                    else:
                        print("CARD DATA INVALID\n")
        
        #WRITE NEW CARD
        elif selection == "3":
            print("-" * 10 + "NEW CARD" + "-" * 10)
            print("Prints formatted track contents to input directly on MagCard software.")
            print("You must create a database entry for the individual FIRST before creating a card for them.\n")
            try:
                #get data of customer to write card for
                first_name = input("First name: ").upper().strip()
                if len(first_name) == 0:
                    raise Exception()
                surname = input("Surname: ").upper().strip()
                if len(surname) == 0:
                    raise Exception()
                university_id = input("University ID (enter blank if none): ").upper().strip()
                #TODO grab this from the database instead!
                #TODO if search returns no results, then add new entry to database
                ricewine_id = input("RiceWine ID (MUST match database!): ").upper().strip()
                if len(ricewine_id) == 0 or not(ricewine_id.isnumeric()):
                    raise Exception()
                date = datetime.date.fromisoformat(input("Expiry Date (Format: YYYY-MM-DD): "))

                #output card data, formatted (must be input manually on external software)
                print("\nEnter these into the corresponding fields on MagCard:\n")
                print("Track 1:")
                print(first_name + "," + surname + ":" + university_id)
                print("Track 2:")
                print(ricewine_id)
                print("Track 3:")
                print(str(date.day) + "0000" + str(date.month) + "0000" + str(date.year))

                input("\nPress enter to continue...\n")
            except:
                print("Invalid data. Operation cancelled.\n")

#refresh database
#TODO back the table up somewhere (backup folder?)
def new_table():
    sql.execute("DROP TABLE IF EXISTS customers;")
    sql.execute("CREATE TABLE customers "
                "(id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "last_name VARCHAR, first_name VARCHAR, "
                "university_id VARCHAR DEFAULT NULL, "
                "expiry DATE, "
                "times_used INTEGER DEFAULT 0, "
                "UNIQUE(last_name, first_name, university_id) "
                ");")
    con.commit()

    print("Database reset.\n")

#print table contents
def print_table():
    print("-" * 10 + "DISPLAYING TABLE" + "-" * 10)

    #show table size
    print()
    print("[" + str(table_size()) + " ENTRIES]\n")

    #show table columns
    for column in sql.execute("SELECT name FROM PRAGMA_TABLE_INFO('customers');"):
        print(column[0], end = "; ")
    print()

    #show table entries
    #TODO find a better table solution (tabbing is ugly!)
    for entry in sql.execute("SELECT * FROM customers;"):
        print(entry[0], end = ": ")
        print(entry[1], end = ", ")
        print(entry[2], end = ";\t\t")
        print(entry[3], end = "; ")
        print(entry[4], end = "; ")
        print(entry[5])
    input("\nPress enter to continue...\n")

#returns integer of number of elements of table
def table_size():
    sql.execute("SELECT COUNT(*) FROM customers")
    return sql.fetchone()[0]

#adds a new entry to table, given data of person to add
def add_to_table(first_name, last_name, university_id):
    presize = table_size()
    sql.execute("INSERT OR IGNORE INTO customers (last_name, first_name, university_id) "
                "VALUES (?, ?, ?);", (last_name.upper().strip(), first_name.upper().strip(), university_id.upper().strip()))
    con.commit()
    if table_size() > presize:
        print("ADDED " + first_name + " " + last_name + " (ID: " + university_id + ")")

#handles the adding of new entries to table
def add_to_table_handler():
    selection = ""
    while selection != "r":
        print("-" * 10 + "ADDING TO TABLE" + "-" * 10)
        print("1: Add single entry via terminal")
        print("2: Add multiple entries from .csv file")
        #TODO add person from card!
        print("R: Return to parent menu")
        print()
        selection = input().lower().strip()

        #inserting a single entry via terminal  
        if selection == "1":
            #get data of customer to add
            first_name, last_name, university_id = "", "", ""
            print()
            while first_name == "":
                first_name = input("First name: ")
            while last_name == "":
                last_name = input("Last name: ")
            university_id = input("University ID (enter blank if none): ")

            #perform addition to table
            selection = ""
            while selection not in ["y", "n"]:
                selection = input("\nProceed with operation? Y/N\n").lower().strip()
            if selection == "y":
                print()
                add_to_table(first_name, last_name, university_id)
                print()
            else:
                print("Operation cancelled.\n")
        
        #inserting multiple entries from a csv file
        elif selection == "2":
            print("\nAccepts only .csv files with 2 fields: one for full name (\"surname,firstname\"), and one for University ID (blank if none).")
            filepath = input("File to open (place in same folder as application): ").strip()
            if len(filepath) > 4 and filepath[-4:] == ".csv":
                entries_to_add = []
                try:
                    with open(filepath, newline = "") as file:
                        reader = csv.reader(file, quotechar = "\"")
                        #skip header
                        next(reader, None)

                        #read data from file
                        for row in reader:
                            name = row[0].split(", ")
                            entries_to_add.append([name[1], name[0], row[1]])
                        
                        #add data to table
                        print()
                        if len(entries_to_add) > 0:
                            for entry in entries_to_add:
                                add_to_table(entry[0], entry[1], entry[2])
                        else:
                            print("No data in file!")
                except:
                    print("Invalid data or file content format!")
            else:
                print("Invalid file or filename!")
            
            print()
    return

def remove_from_table(first_name, last_name, university_id):
    if university_id == "":
        sql.execute("DELETE FROM customers "
                "WHERE last_name = ? AND first_name = ? AND university_id = NULL;", (last_name.upper().strip(), first_name.upper().strip()))
    else:
        sql.execute("DELETE FROM customers "
                    "WHERE last_name = ? AND first_name = ? AND university_id = ?;", (last_name.upper().strip(), first_name.upper().strip(), university_id.upper().strip()))
    con.commit()
    print("REMOVED ALL MATCHING ENTRIES FOR \"" + first_name + " " + last_name + "\" (ID: " + university_id + ")")

def remove_from_table_handler():
    selection = ""
    while selection != "r":
        print("-" * 10 + "REMOVING FROM TABLE" + "-" * 10)
        print("1: Remove single entry via terminal")
        print("R: Return to parent menu")
        print()
        selection = input().lower().strip()

        if selection == "1":
            #get data of customer to remove
            first_name, last_name, university_id = "", "", ""
            print()
            while first_name == "":
                first_name = input("First name: ").upper().strip()
            while last_name == "":
                last_name = input("Last name: ").upper().strip()
            university_id = input("University ID (enter blank if none): ").upper().strip()

            #check how many entries match
            sql.execute("SELECT COUNT(*) FROM customers "
                        "WHERE last_name = ? AND first_name = ? AND university_id = ?;", (last_name, first_name, university_id))
            num_match = sql.fetchone()[0]

            if num_match == 0:
                print("No entries found.\n")

            #perform removal from table if entries found
            else:
                selection = ""
                while selection not in ["y", "n"]:
                    selection = input("\n"+ str(num_match) + " entries found!\nRemove all matching entries from table? Y/N\n").lower().strip()
                if selection == "y":
                    print()
                    remove_from_table(first_name, last_name, university_id)
                    print()
                else:
                    print("Operation cancelled.\n")
    return

def search_edit_handler():
    print("Currently unimplemented. For now, use manage database -> view all entries.\n")
    # "leave blank if don't want to search term"
    # then build up search string with AND in between, and tuple to pass through
    # check if 1 result, if so then ask edit? y/n or maybe have edit/search mode at beginning

if __name__ == "__main__":
    main()

# TODO: new card -> table; table -> card?
# TODO: for editing: get vals and replace into with them
# TODO: will ken have to write manually? ask him to show the program (write from file etc)
# TODO: manual backup?