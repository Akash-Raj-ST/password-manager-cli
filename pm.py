#!/usr/bin/env python

import argparse
from getpass import getpass
import hashlib
import pyperclip

import utils.add
import utils.retrieve
import utils.generate
import utils.update
from utils.dbconfig import dbconfig

from rich import print as printc


class keyValue(argparse.Action):
    # Constructor calling
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, dict())

        for value in values:
            # split it into key and value
            key, value = value.split('=')
            # assign into dictionary
            getattr(namespace, self.dest)[key] = value

parser = argparse.ArgumentParser(description='Description')

parser.add_argument('option', help='(a)dd / (e)xtract / (up)date / (g)enerate')
parser.add_argument("-s", "--name", metavar='', help="Site name")
parser.add_argument("-l", "--url", metavar='', help="Site URL")
parser.add_argument("-e", "--email", metavar='', help="Email")
parser.add_argument("-u", "--user", metavar='', help="Username")
parser.add_argument("-k", "--key", metavar='', help="Key")
parser.add_argument("-v", "--value", metavar='', help="Value")
parser.add_argument('-kv', nargs='*', action=keyValue, help="key value pair")
parser.add_argument('-pkv', nargs='+', help="Protected key value pair")
parser.add_argument("--extra", metavar='',help="Additional password protection")
parser.add_argument("--length", metavar='',help="Length of the password to generate", type=int)
parser.add_argument("-c", "--copy", action='store_true',help='Copy password to clipboard')
parser.add_argument("-ct", "--copyt",help='type of password to copy')


args = parser.parse_args()


def inputAndValidateMasterPassword():
	mp = getpass("MASTER PASSWORD: ")
	hashed_mp = hashlib.sha256(mp.encode()).hexdigest()
	
	client = dbconfig()
	db = client["pm"]
	secretCollection = db["secrets"]
	result = secretCollection.find()

	if hashed_mp != result[0]["masterkey_hash"]:
		printc("[red][!] WRONG! [/red]")
		return None

	return [mp, result[0]["ds"]]

def main():
	if args.option in ["add", "a"]:
		if args.name == None or args.url == None or args.user == None:
			if args.name == None:
				printc("[red][!][/red] Site Name (-s) required ")
			if args.user == None:
				printc("[red][!][/red] Site USER (-u) required ")
			return

		if args.email == None:
			args.email = ""
		
		if args.url == None:
			args.url = ""

		res = inputAndValidateMasterPassword()
		data = {}
		if res is not None:
			data["site"] = args.name
			data["url"] = args.url
			data["username"] = args.user
			data["email"] = args.email
			data["additional"] = {}
			if args.kv:
				for key in args.kv:
					data["additional"][key] = args.kv[key]

			if(utils.add.checkEntry(args.name,args.email)):
				printc("[yellow][-][/yellow] Entry with these details already exists")
				return

			data["passwords"] = {}
			data["passwords"]["password"] = utils.add.get_password(res[0], res[1], "site")

			if args.pkv:
				for key in args.pkv:
					data["passwords"][key] = utils.add.get_password(res[0], res[1], key)

			utils.add.addEntry(res[0], res[1], data)

	elif args.option in ["extract","e"]:
		# if args.name == None and args.url == None and args.email == None and args.user == None:
		# 	# retrieve all
		# 	printc("[red][!][/red] Please enter at least one search field (sitename/url/email/username)")
		# 	return
		res = inputAndValidateMasterPassword()
			
		search = {}
		if args.name is not None:
			search["site"] = args.name
		if args.url is not None:
			search["url"] = args.url
		if args.email is not None:
			search["email"] = args.email
		if args.user is not None:
			search["username"] = args.user

		if res is not None:
			if args.copyt is not None:
				utils.retrieve.retrieveEntries(res[0],res[1],search,decryptPassword = args.copy,passwordType=args.copyt)
			else:
				utils.retrieve.retrieveEntries(res[0],res[1],search,decryptPassword = args.copy)

	elif args.option in ["update","up"]:
		res = inputAndValidateMasterPassword()

		search = {}
		if args.name is not None:
			search["site"] = args.name
		if args.url is not None:
			search["url"] = args.url
		if args.email is not None:
			search["email"] = args.email
		if args.user is not None:
			search["username"] = args.use

		if res is not None:
			utils.update.updateEntry(res[0], res[1], search)

	elif args.option in ["generate","g"]:
		if args.length == None:
			printc("[red][+][/red] Specify length of the password to generate (--length)")
			return
		password = utils.generate.generatePassword(args.length)
		pyperclip.copy(password)
		printc("[green][+][/green] Password generated and copied to clipboard")



main()
