#mozda ima razlicitih favicona na razlicitim assetima

from netaddr import iter_iprange
import urllib2
import hashlib
import sys
import ssl
import threading
#from getch import getch
import msvcrt

timeout=1
threads=1
finished=0
processed=0

#To disable ssl verification because we are accessing hosts via IP addresses
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

#Get original favicon/hash
for protocol in ('http://','https://'):
	try:
		hash1=hashlib.md5(urllib2.urlopen(protocol+sys.argv[1]+'/favicon.ico').read()).hexdigest()
		break
	except:
		if (protocol=='https://'):
			print "Can not find favicon on "+sys.argv[1]
			exit()

#For locking ip generator / making it threadsafe
class LockedIterator(object):
    def __init__(self, it):
        self.lock = threading.Lock()
        self.it = it.__iter__()

    def __iter__(self): return self

    def next(self):
        self.lock.acquire()
        try:
            return self.it.next()
        finally:
            self.lock.release()

generator = LockedIterator(iter_iprange(sys.argv[2], sys.argv[3], step=1))

#Comparing favicons
def compare():
	global finished
	global processed
	
	while (finished==0):
		resource=None

		try:
			ip=str(generator.next())
			processed+=1
		except Exception as e: 
			print str(e)
			finished=1
			break

		for protocol in ('http://','https://'):
			try:
				resource = urllib2.urlopen(protocol+ip+'/favicon.ico', context=ctx, timeout=timeout)
				break
			except Exception as e:
				#print str(e)
				continue
				
		if (resource==None):
			continue
			
		try:
			hash2=hashlib.md5(resource.read()).hexdigest()
			resource.close()
			if (hash1==hash2):
				print ip
		except Exception as e:
			#print str(e)
			continue
			
def status():
	global finished
	global processed
	while (finished==0):
		if msvcrt.kbhit():
			msvcrt.getch()
			msvcrt.getch()
			print "Processed "+str(processed)+" ip addresses."
	
#Threading
t1 = threading.Thread(target=status)
t1.start()

for n in range (threads):
    t2 = threading.Thread(target=compare)
    t2.start()

