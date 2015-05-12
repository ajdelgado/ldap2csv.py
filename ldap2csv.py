#!/usr/bin/env python
# Output LDIF info from LDAP server into CSV (semicolon separator) data
# Antonio J. Delgado 2015
# Requires python-ldap (Ubuntu: sudo apt-get install python-ldap)
import ldap,sys

cfg=dict()
cfg['server_uri']="ldap://ldap.domain.com"
cfg['bind_dn']=""
cfg['search_base']="ou=staff,dc=domain,dc=com"
cfg['bind_pw']=""
cfg['filter']="(!(title=*functional*))"
cfg['fields']=['cn','description']

myldap = ldap.initialize('%s' % cfg['server_uri'])
result=myldap.search_s(cfg['search_base'],ldap.SCOPE_SUBTREE,cfg['filter'],cfg['fields'])

records=list()
for dn,entry in result:
	record=dict()
	record['dn']=dn
	for field in cfg['fields']:
		record[field]=""
	for k,values in entry.items():
		for v in values:
			if k in record:
				record[k]="%s\n%s" % (record[k],v)
			else:
				record[k]=v
		if record[k].find("\n")> -1:
			record[k]="\"%s\"" % record[k]
	records.append(record)
sys.stdout.write("dn;")
for field in cfg['fields']:
	sys.stdout.write("%s;" % field)
sys.stdout.write("\n")
for rec in records:
	sys.stdout.write("%s;" % rec['dn'])
	for field in cfg['fields']:
		sys.stdout.write("%s;" % rec[field])
	sys.stdout.write("\n")
