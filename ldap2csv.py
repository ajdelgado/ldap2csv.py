#!/usr/bin/env python
# Output LDIF info from LDAP server into CSV (semicolon separator) data
# Antonio J. Delgado 2015
# Requires python-ldap (Ubuntu: sudo apt-get install python-ldap)
import ldap,sys

cfg=dict()
cfg['server_uri']=""
cfg['bind_dn']=""
cfg['search_base']=""
cfg['bind_pw']=""
cfg['filter']=""
cfg['fields']=list()
DEBUG=0

def Usage():
	print "-u | --uri			URI to connect to (like ldaps://ldap.domain.com:389)"
	print "-d | --bind-dn		Bind distinguised name to connect as"
	print "-b | --bind-pw		Password of the binded DN"
	print "-s | --search-base	Search base DN (like dc=domain,dc=com)"
	print "-f | --filter		LDAP filter (like (uid=username))"
	print "-l | --fileds		LDAP fields to show, if omited all fields will be show"
	print "-v					Verbose output, repeat it to increase verbosity"
	print "-h					Show this help"
def Message(TEXT,Force=False):
	global DEBUG
	if DEBUG > 0 or Force:
		print TEXT
	
def GetArguments():
	import getopt
	global DEBUG,cfg
	try:
		opts, args = getopt.getopt(sys.argv[1:], "u:d:s:b:f:l:vh", ["uri=", "bind-dn=", "search-base=", "bind-pw=", "filter=", "fields="])
	except getopt.GetoptError as err:
		print str(err)
		Usage()
		sys.exit(65)
	output = None
	verbose = False
	for o, a in opts:
		if o == "-v":
			DEBUG=DEBUG+1
		elif o in ("-h", "--help"):
			Usage()
			sys.exit()
		elif o in ("-u", "--uri"):
			Message("Server URI will be %s" % a)
			cfg['server_uri']=a
		elif o in ("-d", "--bind-dn"):
			Message("Bind DN will be %s" % a)
			cfg['bind_dn']=a
		elif o in ("-b", "--bind-pw"):
			Message("Bind password will be '***'")
			cfg['bind_pw']=a
		elif o in ("-s", "--search-base"):
			Message("Search base will be %s" % a)
			cfg['search_base']=a
		elif o in ("-f", "--filter"):
			Message("Filter will be %s" % a)
			cfg['filter']=a
		elif o in ("-l", "--fields"):
			Message("Another field to show will be %s" % a)
			cfg['fields'].append(a)
		else:
			assert False, "unhandled option %s" % o
def ListOfDicts2CSV(ListOfDicts,FileDescriptor):
	import csv
	fieldnames=list()
	for dItem in ListOfDicts:
		for key in dItem.iterkeys():
			if not key in fieldnames:
				fieldnames.append(key)
	with FileDescriptor as csvfile:
		writer=csv.DictWriter(csvfile,delimiter=';',quotechar="\"",fieldnames=fieldnames)
		writer.writeheader()
		writer.writerows(ListOfDicts)
def _main():
	GetArguments()
	if cfg['server_uri'] == "" or cfg['search_base'] == "":
		print "Please at least indicate the URI to connect to and the base DN to search for."
		Usage()
		sys.exit(65)
	try:
		myldap = ldap.initialize('%s' % cfg['server_uri'])
	except ldap.LDAPError,e:
		Message("Error connecting to '%s'. %s" % (cfg['server_uri'],e),True)
		sys.exit(1)
	try:
		result=myldap.search_s(cfg['search_base'],ldap.SCOPE_SUBTREE,cfg['filter'],cfg['fields'])
	except ldap.NO_SUCH_OBJECT,e:
		Message("Error searching for the fields '%s' in the base DN '%s' with the filter '%s'" % (cfg['fields'],cfg['search_base'],cfg['filter']),True)
		sys.exit(0)
	records=list()
	for dn,entry in result:
		record=dict()
		for k,values in entry.items():
			for v in values:
				if k in record:
					record[k]="%s\n%s" % (record[k],v)
				else:
					record[k]=v
			if record[k].find("\n")> -1:
				record[k]="\"%s\"" % record[k]
		records.append(record)
	ListOfDicts2CSV(records,sys.stdout)
_main()
