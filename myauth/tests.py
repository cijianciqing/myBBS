from django.test import TestCase

# Create your tests here.

import os
import django
import logging
from myBBS import settings

if __name__ == '__main__':
   os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myBBS.settings')
   django.setup()

   aa =  os.path.join(settings.BASE_DIR, '/myUpload/myImage/default.png')
   print(aa)