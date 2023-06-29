
import os
import time

current_time = time.time()
directory = '/var/www/html'

#add cron job for this file - cronatb -e in linux
#files in directory will delete after 90 min automatically

for root,dirs,files in os.walk(directory):
     for file_name in files:
          path = '%s/%s'%(root,file_name)
          creation_time = os.path.getctime(path)
          if current_time - creation_time > (90*60):
              os.remove(path)
