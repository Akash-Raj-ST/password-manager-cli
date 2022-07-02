import os
import sys
import string
import random
import hashlib
import sys
from getpass import getpass

from utils.dbconfig import dbconfig

from rich import print as printc
from rich.console import Console


def checkConfig():
    client = dbconfig()
    dblist = client.list_database_names()
    if "pm" in dblist:
        return True
    return False

def generateDeviceSecret(length=10):
	return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def dbConfig():
  
    if checkConfig():
        printc("[red][!] Already Configured! [/red]")
        return

    printc("[green][+] Creating new config [/green]")

	# Create database
    client = dbconfig()
    
    try:
        #create db
        db = client["pm"]

    except Exception as e:
	    printc("[red][!] An error occurred while trying to create db. Check if database with name 'pm' already exists - if it does, delete it and try again.")
	    console.print_exception(show_locals=True)
	    sys.exit(0)

    printc("[green][+][/green] Database 'pm' created")

	# Create tables
    secretCollection = db["secrets"]
    printc("[green][+][/green] Table 'secrets' created ")

    dataCollection = db["data"]
    printc("[green][+][/green] Table 'entries' created ")

    mp = ""
    printc("[green][+] A [bold]MASTER PASSWORD[/bold] is the only password you will need to remember in-order to access all your other passwords. Choosing a strong [bold]MASTER PASSWORD[/bold] is essential because all your other passwords will be [bold]encrypted[/bold] with a key that is derived from your [bold]MASTER PASSWORD[/bold]. Therefore, please choose a strong one that has upper and lower case characters, numbers and also special characters. Remember your [bold]MASTER PASSWORD[/bold] because it won't be stored anywhere by this program, and you also cannot change it once chosen. [/green]\n")

    while 1:
        mp = getpass("Choose a MASTER PASSWORD: ")
        if mp == getpass("Re-type: ") and mp != "":
	        break
        printc("[yellow][-] Please try again.[/yellow]")

	# Hash the MASTER PASSWORD
    hashed_mp = hashlib.sha256(mp.encode()).hexdigest()
    printc("[green][+][/green] Generated hash of MASTER PASSWORD")


	# Generate a device secret
    ds = generateDeviceSecret()
    printc("[green][+][/green] Device Secret generated")

	# Add them to db
    master_password = {
        "masterkey_hash": hashed_mp,
        "ds": ds
    }
    secretCollection.insert_one(master_password)

    printc("[green][+][/green] Added to the database")

    printc("[green][+] Configuration done![/green]")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("argv needed!!")
        sys.exit(0)

    if sys.argv[1] == "init":
        dbConfig()
    else:
        print("Usage: python config.py init")
