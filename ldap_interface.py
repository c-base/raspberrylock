#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import base64
import hashlib
from datetime import datetime

from lmap import *

import config


def ldap_connect():
	ld = ldap.ldap(config.LDAP.URI)
	ld.simple_bind(config.LDAP.BINDDN, config.LDAP.BINDPW)
	return lmap.lmap(dn=config.LDAP.BASE, ldap=ld)


def pwcheck(record, pw):
	if not record.startswith('{SSHA}'):
		return record == pw
	bd = base64.b64decode(bytearray(record[6:], 'UTF-8'))
	hashv = bd[:20]
	salt = bd[20:]
	newhashv = hashlib.sha1(bytearray(pw, 'UTF-8')+salt).digest()
	return hashv == newhashv


def authenticate(uid, pin):
	lm = ldap_connect()
	try:
		user = lm(config.LDAP.USERBASE).search(config.LDAP.ACCESS_FILTER.format(uid))[0]
		username = user[config.LDAP.UIDFIELD]
		if pwcheck(user[config.LDAP.PINFIELD], pin):
			print(datetime.now(), 'Valid combination for user "%s". Opening lock' % username)
			return True
	except Exception as e:
		print(datetime.now(), 'Invalid user/pin:', uid, '('+str(e)+')')
	return False


numbuf = []


if __name__ == "__main__":
	print(pwcheck('{SSHA}c8pLDYbSkF2jBAKxxa67nY7NYkdQXiPNFzzRso9FRZI=', '1234'))

