#!/usr/bin/env python
import sys, time
from os import listdir
from os.path import isfile, join
import shutil
from daemon import Daemon
import os
from settings import *
from subprocess import call

def read_in_chunks2(file_object, target_file,chunk_size=1024):
    """Lazy function (generator) to read a file piece by piece.
    Default chunk size: 1k."""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data


class HomeCloud(Daemon):
	def run(self):
		while True:
			print 'Syncing folders...' 
               		mypath = SYNC_FOLDER
			drive = DRIVE_FOLDER

			remote_files = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]
			local_files = [ f for f in listdir(drive) if isfile(join(drive,f)) ]

			counter = 0
			
			for file in remote_files:
				if ( file not in local_files ):
					statinfo = os.stat(mypath+file)
					if (statinfo.st_size < MAX_FILE_SIZE*1024):
						shutil.copy(mypath+file, drive+file)
					else:
						part = 0
						f = open(mypath+file)
						f2 = open(drive+file+'.part'+str(part),'w+')	
						#using yield and generator to reduce memory consumption, 
						#I think.. :)
						for piece in read_in_chunks2(f,f2):
							counter = counter + 1
							f2.write(piece)
							#divide file based on MAX_FILE_SIZE
							if ( counter >= MAX_FILE_SIZE ):
								counter = 0
								part = part + 1
                	                                        f2.close()
								f2 = open(drive+file+'.part'+str(part),'w+')
								#useless try to clean the memory while copying
								call(["sync"])
								call(["sysctl", "-w", "vm.drop_caches=3"])	
					'''shutil.copy(mypath+file, drive+file)'''
					print "created: %s" % time.ctime(os.path.getctime(mypath+file))
					if (REMOVE_ORIGINAL):
						os.remove(mypath+file)
				elif (os.path.getmtime(mypath+file) < os.path.getmtime(mypath+file) ):
					shutil.copy(mypath+file, drive+file)    
			time.sleep(SYNC_FREQUENCY)
 
if __name__ == "__main__":
        daemon = HomeCloud('/tmp/homecloud-daemon.pid')
        if len(sys.argv) == 2:
                if 'start' == sys.argv[1]:
 			daemon.start()
                elif 'stop' == sys.argv[1]:
                        daemon.stop()
                elif 'restart' == sys.argv[1]:
                        daemon.restart()
                else:
                        print "Unknown command"
                        sys.exit(2)
                sys.exit(0)
        else:
                print "usage: %s start|stop|restart" % sys.argv[0]
                sys.exit(2)

