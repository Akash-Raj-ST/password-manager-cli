from utils.dbconfig import dbconfig

import utils.aesutil
import pyperclip
from pandas import DataFrame
from getpass import getpass

from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA512
from Crypto.Random import get_random_bytes
import base64

from rich import print as printc
from rich.console import Console
from rich.table import Table



def computeMasterKey(mp, ds):
	password = mp.encode()
	salt = ds.encode()
	key = PBKDF2(password, salt, 32, count=1000000, hmac_hash_module=SHA512)
	return key


def get_password(mp, ds, password):

	# compute master key
	mk = computeMasterKey(mp, ds)

	# encrypt password with mk
	encrypted = utils.aesutil.encrypt(key=mk, source=password, keyType="bytes")
	return encrypted

def updateEntry(mp, ds, search):

    ''' Find the unique entry    '''

    client = dbconfig()
    db = client["pm"]
    dataCollection = db["data"]

    query = ""

    if len(search) == 0:
        cur = dataCollection.find()
    else:
        cur = dataCollection.find(search)

    results = list(cur)

    console = Console()

    if len(results) == 0:
        printc("[yellow][-][/yellow] No results for the search")
        return
    
    elif len(results) > 1:
        printc("[yellow][-][/yellow] More than one result found for the search. Be more specific.")
        
        table = Table(title="Results")
        table.add_column("Site Name")
        table.add_column("Email")
        table.add_column("Username")
        table.add_column("Password")

        for i in results:
            table.add_row(i["site"], i['email'], i["username"], "{hidden}")

        console.print(table)
    
    else:
        printc("[yellow][-][/yellow] Press enter if change not needed.")

        result = results[0]

        printc(f"Enter Site name [yellow][?]{result['site']}[/yellow] : ")
        new_site = input()

        printc(f"Enter Email [yellow][?]{result['email']}[/yellow] : ")
        new_email = input()

        printc(f"Enter Username [yellow][?]{result['username']}[/yellow] : ")
        new_user = input()

        printc(f"Enter URL [yellow][?]{result['url']}[/yellow] : ")
        new_url = input()

        new_additional = {}
        if result['additional'] is not None:
            for i in result['additional']:
                printc(f"Enter {i} [yellow][?]{result['additional'][i]}[/yellow]")
                in_data = input()
                new_additional[i] = in_data if len(in_data)>0 else result['additional'][i]

        new_passwords = {}
        if result['passwords'] is not None:
            for i in result['passwords']:
                printc(f"Enter {i} [red][?]hidden[/red]")
                in_data = getpass("")
                new_passwords[i] = get_password(mp,ds,in_data) if len(in_data) > 0 else result['passwords'][i]
        
        new_data = {
            'site':new_site if len(new_site)>0 else result['site'],
            'email': new_email if len(new_email) > 0 else result['email'],
            'username': new_user if len(new_user) > 0 else result['username'],
            'url':new_url,
            'additional':new_additional,
            'passwords':new_passwords
        }

        dataCollection.replace_one(search, new_data)
        printc("[green][+][/green] Entry Updated ")

            
