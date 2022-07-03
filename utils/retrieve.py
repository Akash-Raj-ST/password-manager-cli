from utils.dbconfig import dbconfig

import utils.aesutil
import pyperclip
from pandas import DataFrame

from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA512
from Crypto.Random import get_random_bytes
import base64

from rich import print as printc
from rich.console import Console
from rich.table import Table

def computeMasterKey(mp,ds):
	password = mp.encode()
	salt = ds.encode()
	key = PBKDF2(password, salt, 32, count=1000000, hmac_hash_module=SHA512)
	return key

def retrieveEntries(mp, ds, search, decryptPassword = False, passwordType="password"):

	client = dbconfig()
	db = client["pm"]
	dataCollection = db["data"]

	query = ""
	
	if len(search)==0:
		cur = dataCollection.find()
	else:
		cur = dataCollection.find(search)
	
	results = list(cur)

	if len(results) == 0:
		printc("[yellow][-][/yellow] No results for the search")
		return


	console = Console()
	if (decryptPassword and len(results)>1) or (not decryptPassword):
		if decryptPassword:
			printc("[yellow][-][/yellow] More than one result found for the search, therefore not extracting the password. Be more specific.")
		table = Table(title="Results")
		table.add_column("Site Name")
		table.add_column("Email")
		table.add_column("Username")
		table.add_column("Password")

		for i in results:
			table.add_row(i["site"], i['email'], i["username"], "{hidden}")

		
		console.print(table)

	if not decryptPassword and (len(results)==1):
		table2 = Table()
		table2.add_column("KEY")
		table2.add_column("Value")

		if len(results[0]["url"])>0:
			table2.add_row("url", results[0]["url"])

		for i in results[0]["additional"]:
			table2.add_row(i, results[0]["additional"][i])

		for i in results[0]["passwords"]:
			table2.add_row(i, "{hidden}")

		console.print(table2)

	if decryptPassword and len(results)==1:
		# Compute master key
		mk = computeMasterKey(mp,ds)

		# decrypt password
		if passwordType in results[0]["passwords"]:
			decrypted = utils.aesutil.decrypt(key=mk,source=results[0]["passwords"][passwordType],keyType="bytes")

			printc("[green][+][/green] Password copied to clipboard")
			pyperclip.copy(decrypted.decode())
		else:
			printc("[red][+][/red] no such password type exists")

def retrieveEntriesByID(mp, ds, id, decryptPassword=False):
	pass
