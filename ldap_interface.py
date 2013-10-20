#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import hashlib
from lmap import *

import config


def ldap_connect():
	ld = ldap.ldap(config.LDAP.URI)
	ld.simple_bind(config.LDAP.BINDDN, config.LDAP.BINDPW)
	return lmap.lmap(dn=config.LDAP.BASE, ldap=ld)

def pwcheck(record, pw):
	if not record.startswith('{SSHA}'):
		return record == pw
	bd = base64.b64decode(bytes(record[6:], 'UTF-8'))
	hashv = bd[:20]
	salt = bd[20:]
	newhashv = hashlib.sha1(bytes(pw, 'UTF-8')+salt).digest()
	return hashv == newhashv

def authenticate(uid, pin):
	lm = ldap_connect()
	try:
		user = lm(config.LDAP.USERBASE).search(config.LDAP.ACCESS_FILTER.format(uid))[0]
		if pwcheck(user[config.LDAP.PINFIELD], pin):
			return True
	except Exception as e:
		print('Invalid user/pin:', uid, '('+str(e)+')')
	return False

numbuf = []

