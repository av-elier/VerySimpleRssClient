# coding = UTF-8
'''
Created on 18 окт. 2013 г.

@author: Adelier
'''

from RssFeedImpl import update_all_feeds
from RssTkinkerGui import RssTkinkerGui

import time
import _thread
            
if __name__ == '__main__':
    def autoupdate(time_interval):
        while True:
            try:
                update_all_feeds()
            except:
                print("no internet connection")
            time.sleep(time_interval)
    updateThread = _thread.start_new_thread( autoupdate, (60*5,) )
    
    gui = RssTkinkerGui()
    gui.launch()