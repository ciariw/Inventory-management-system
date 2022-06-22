# - create a data structure for parts that includes reference images, material code and usage details
# - initial items can be categorized using the machine
# - items are referenced
# - Generate database to be used for storage and querying data
#
# Later goals:
# - include image recognition
# - include GUI for displaying images and names. Train based on selection
# - quick scan
import json
import heapq
import time
import psycopg2
import glob
from pathlib import Path
from generate_parts_object import load_workbook_data

PATH = Path(__file__)


class Inventory:

    def __init__(self):
        self.cursor = None
        self.last_query_result = None
        self.connected = False # Default value
        self.connection = None
        if not (PATH.parent/'Parts.JSON').exists():
            temp_items = load_workbook_data()
            with open('Parts.JSON', 'w') as file:
                json.dump(temp_items,file,indent=4)

        # Only generates a JSON when there isnt one. load local object for reference
        with open(PATH.parent/'Parts.JSON', encoding="utf-8") as j:
            self.items = json.load(j)

    # Connect to the Database
    def db_connect(self,db:str):
        if self.connection:
            # Avoid multiple sessions
            self.connected = True
            return self
        ## Temporary override
        self.connection = psycopg2.connect(
            database=f"{db}",
            user="postgres"
        )
        self.cursor = self.connection.cursor()
        if type(self.connection) == psycopg2.extensions.connection:
            # Validate that the selected connection object is a psycopg connection object
            # If so, change the status to connected
            self.connected = True
        return self

    # Execute a command on the Database (Command not validated)
    def db_exec_cmd(self,command:str, print_result = False)->None:
        if not self.connection or not self.connected:
            print(f"Connection status: {self.connection}\n Connected: {self.connected}")
            return self
        connection = self.connection
        cursor = self.cursor
        # referencing
        cursor.execute(command)
        self.last_query_result = cursor.fetchall()
        if print_result:
            print(self.last_query_result)

    # Check if all items in the dictionary are in the database
    def db_validate(self,items:dict,*depth):

        if not self.connected:
            # If you aren't connected to the db, return
            print("not connected to the Database")
            return self

        cursor = self.cursor
        if items is None or not items.keys():
            print("not enough items in items dictionary")
            return self

        if depth:
            # Something here to leave open the chance for a deep search.
            # Validates that all values in the 'items' dict reflect in the DB.
            # Deep search checks and flags any differences.
            # Prompts to update DB, updates the DB and does another check
            print(depth)

        # Will be deprecated in the future in exchange for search depth logic
        for i in items:
            cursor.execute(
                f"SELECT id FROM genmaterials WHERE id = {i}"
            )
            fetchres = cursor.fetchone()
            if fetchres:
                self.last_query_result = fetchres
            else:
                cursor.execute("INSERT INTO genmaterials "  # insert into the genmaterials table
                               "(id,description,vendor,energy,location,machine, vendorID) VALUES "  # Insert these columns
                               f"(%s,%s,%s,%s,%s,%s,%s);",
                               [i, items[i]['Description'], items[i]['Company'],
                                items[i]['type'], items[i]['Location'], items[i]['Machine'],
                                items[i]['Vendor ID']])
                print("New entry created")
                # If the item isnt in there, add the item to the db. Dangerous
        return self

    def db_disconnect(self):
        if not self.connection:
            print("Strange behavior")
            return self
        self.connection.commit()
        self.cursor.close()
        self.connection.close()
        self.connected = False
        return self

    def _update_inventory(self):

        return

    def db_item_search(self,keyword:set):
        if not self.connected or not self.connection:
            print('brokeboy')
            return self
        cursor = self.cursor
        # Building command
        alias = ' OR description ILIKE '.join([f"'{x}%'" for x in keyword])
        cursor.execute(f'SELECT * FROM genmaterials WHERE description ILIKE {alias};')
        self.last_query_result = cursor.fetchall()
        print(self.last_query_result)

        return self


def main():

    inventory = Inventory()  # Create inventory object and load materials json
    inventory.db_connect("inventory")  # Connect to the database 'inventory'

    #inventory.db_validate(inventory.items)
    # validate that materials json and database entries match

    #inventory.db_item_search({"M"})  # Search for items that contain words in this set
    inventory.db_exec_cmd("SELECT distinct vendor FROM genmaterials WHERE machine ILIKE 'LAMINATOR';",False)
    print("\n".join([str(x) for x in inventory.last_query_result]))
    inventory.db_disconnect()  # Disconnect everything and start fresh




if __name__ == '__main__':

    main()
