from pymongo import MongoClient
import pymongo

from rich import print as printc
from rich.console import Console
console = Console()

import sys
from .password import db_password

def dbconfig():
  try:
    CONNECTION_STRING = f"mongodb+srv://akash_raj_st:{db_password}@cluster0.1wid5.mongodb.net/?retryWrites=true&w=majority"
    
    client = MongoClient(CONNECTION_STRING)
    dblist = client.list_database_names()
    return client

  except:
    print("[red][!] An error occurred while trying to connect to the database[/red]")
    console.print_exception(show_locals=True)
    sys.exit(0)
