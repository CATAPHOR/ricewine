import re
import sqlite3

#initialise sqlite interface
con = sqlite3.connect("ricewine.db")
sql = con.cursor()

#Person class encapsulates database entry
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

    #given input, assign attributes of person 
    def assign_attributes(self, firstname, surname, university_id, expiry_date):
        if len(firstname) == 0 or len(surname) == 0 or len(university_id):
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
    while selection not in ["1", "2", "q"]:
        print("-" * 10 + "ROOT MENU" + "-" * 10)
        print("Type number to select mode:")
        print("1: Manage database")
        print("2: Verify against database")
        print("Q: Quit application")
        selection = input("\n").lower()
        
        #QUIT
        if selection == "q":
            con.close()
            selection = ""
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
                print("4: Search/edit database entry")
                print("X: Reset database [DANGER]")
                print("R: Return to parent menu")
                selection = input("\n").lower()
                #return to previous menu
                if selection == "r":
                    pass
                #print all database entries
                elif selection == "1":
                    print_table()
                #reset database
                elif selection == "x":
                    selection = ""
                    while selection not in ["y", "n"]:
                        selection = input("\nAre you sure? This will delete ALL data. Y/N\n").lower()
                    if selection == "y":
                        new_table()
            
        #VERIFY AGAINST DATABASE
        elif selection == "2":
            # TODO: handle IO (reader writes to file, or reader outputs as keyboard input?)
            # take input (has to be able to keep taking it until stoppage)
            # display whether valid
            #TESTING
            input_text = ("%KEN,YANAGIDA:K1892327?" +
                          ";123456789?" +
                          "+1100001100002000?")

            testguy = Person()
            if testguy.read_card(input_text):
                testguy.output_attributes()
            else:
                print("Invalid data!\n")
            selection = ""
            input()

def new_table():
    #TODO remove existing table
    sql.execute("DROP TABLE IF EXISTS customers;")
    sql.execute("CREATE TABLE customers "
                "(id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "last_name VARCHAR, first_name VARCHAR, "
                "university_id VARCHAR, "
                "expiry DATE, "
                "times_used INTEGER DEFAULT 0"
                ");")
    con.commit()

    print()

def print_table():
    print()

if __name__ == "__main__":
    main()

# TODO: handle invalid patterns/vals (ValueError??)

