from utils.dbconfig import dbconfig
import utils.aesutil
from getpass import getpass

from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA512
from Crypto.Random import get_random_bytes
import base64

from rich import print as printc
from rich.console import Console

def computeMasterKey(mp,ds):
	password = mp.encode()
	salt = ds.encode()
	key = PBKDF2(password, salt, 32, count=1000000, hmac_hash_module=SHA512)
	return key


def checkEntry(siteName,email):

	client = dbconfig()
	db = client["pm"]
	dataCollection = db["data"]

	# Check if the entry already exists
	dataItems = dataCollection.find()

	for items in dataItems:
		if items["site"]==siteName and items["email"]==email:
			return True
	return False


def addEntry(mp, ds, data):

	# Add to db
	client = dbconfig()
	db = client["pm"]
	dataCollection = db["data"]
	dataCollection.insert_one(data)
	
	printc("[green][+][/green] Added entry ")

def get_password(mp, ds, type):
	# Input Password
	password = getpass(f"Password for {type}: ")

	# compute master key
	mk = computeMasterKey(mp, ds)

	# encrypt password with mk
	encrypted = utils.aesutil.encrypt(key=mk, source=password, keyType="bytes")
	return encrypted
