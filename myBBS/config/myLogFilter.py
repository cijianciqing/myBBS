# -*- coding: utf-8 -*-#

#-------------------------------------------------------------------------------
# Name:         myLogFilter
# Description:  
# Author:       Administrator
# Date:         2019-11-16
#-------------------------------------------------------------------------------
import logging


class TestFilter(logging.Filter):

    def filter(self, record):
        if '----' in record.msg:
            # false:会被过滤掉
            return False
        else:
            return True
