import main
inventory = main.Inventory()
inventory.db_connect("inventory").db_validate(inventory.items)


def receive_query(message:dict):
    # Super simple proof of concept for now.
    print(f"Hello {message.chat.first_name}, you sent: ",message.text)
    search = set(message.text.split(' '))
    search.add(message.text)
    access_db(search)


def access_db(text:set):
    inventory.db_item_search(text)
    print('that breaks down into: ',inventory.formatted_query)



