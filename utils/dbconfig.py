from pymongo import MongoClient
import pymongo

from rich import print as printc
from rich.console import Console
console = Console()

import sys
from .password import db_password

def dbconfig():
  try:
    CONNECTION_STRING = "mongodb://localhost:27017"
    client = MongoClient(CONNECTION_STRING)
    return client

  except:
    print("[red][!] An error occurred while trying to connect to the database[/red]")
    console.print_exception(show_locals=True)
    sys.exit(0)
