# coding = UTF-8
'''
Created on 17 окт. 2013 г.

@author: Adelier
'''
import xml.etree.ElementTree as etree
import urllib.request

import sqlite3
import os

database = 'rssfeeds.db'

def get_feed_urls_list():
    conn = sqlite3.connect(database)
    res = list()
    for url in conn.cursor().execute('SELECT url FROM feeds'):
        res.append(url[0])
    conn.close()
    return res


def load_from_xml_into_db(url):
    feed = RssFeed()
    feed.load_from_xml_rss(url)
    feed.store_to_database()
    
def update_all_feeds():
    for url in get_feed_urls_list():
        feed = RssFeed()
        print('updating ' + url)
        feed.load_from_xml_rss(url)
        feed.store_to_database()
         
def ensure_db_exists(faliscount = 0):
    if faliscount > 1:
        raise Exception("can't access database")
    try:
        conn = sqlite3.connect(database)
        conn.cursor().execute('''CREATE TABLE IF NOT EXISTS feeds (
            id INTEGER PRIMARY KEY ASC, 
            url VARCHAR  NOT NULL UNIQUE,
            title VARCHAR  NOT NULL, 
            descr VARCHAR)''')
        conn.cursor().execute('''CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY ASC, 
            feed_id INTEGER FOREIN KEY,
            url VARCHAR NOT NULL UNIQUE,
            title VARCHAR NOT NULL,
            content VARCHAR ,
            upd_date INTEGER)''')
        conn.commit()
        conn.close()
    except:
        os.remove(database)
        ensure_db_exists(faliscount + 1)   

class RssItem():
    def __init__(self):
        self.title = None
        self.description = None
        self.pub_date = None
        self.link = None
    
    def load_from_xmlitem(self, xml_item):
        self.title = xml_item.find('title').text
        self.description = xml_item.find('description').text
        self.pub_date = xml_item.find('pubDate').text
        self.link = xml_item.find('link').text
        
        
    '''items (
        id INTEGER, 
        feed_id INTEGER FOREIN KEY,
        url VARCHAR NOT NULL,
        title VARCHAR NOT NULL,
        content VARCHAR ,
        upd_date INTEGER)'''
    def store_to_database(self, conn, feed_id):
        try:
            conn.cursor().execute('''INSERT INTO items (feed_id,url,title,content,upd_date) VALUES( 
                        :feed_id,
                        :url,
                        :title,
                        :content, 
                        :upd_date)''', {'feed_id': feed_id,
                                        'url': self.link,
                                        'title': self.title,
                                        'content': self.description,
                                        'upd_date': self.pub_date})
        except:
            pass
    def load_from_database_res_line(self, sql_line):
        self.link = sql_line[0]
        self.title = sql_line[1]
        self.description = sql_line[2]
        self.pub_date = sql_line[3]
        

class RssFeed:
            
    def __init__(self):
        self.link = None
        self.title = None
        self.description = None
        self.items = None
        ensure_db_exists()
            
    def load_from_xml_rss(self, url):
        url_connection = urllib.request.urlopen(url)
        
        url_stream = url_connection.read()
        
        try:
            self.root = etree.fromstring(url_stream)
        except:
            raise Exception('probably not rss')
        if self.root.tag != 'rss':
            raise Exception('probably not rss')
        self.link = url
        self.channel = self.root.find('channel')
        
        self.title = self.channel.find('title').text
        self.description = self.channel.find('description').text
        
        self.items = list()
        for child in self.channel.findall('item'):
            rss_item = RssItem()
            rss_item.load_from_xmlitem(child)
            self.items.append(rss_item)
        
        url_connection.close()


        
    def store_to_database(self, feed_id=None):
        conn = sqlite3.connect(database)
        
        # ���� �������
        def create_feed_in_db(url, conn, title, descr):
            new_id = None
            try:
                conn.cursor().execute('''INSERT INTO feeds (url,title,descr) VALUES( 
                    :url,
                    :title, 
                    :descr)''', {'url': self.link,
                                 'title': self.title,
                                 'descr': self.description})
                new_id = conn.cursor().execute('''SELECT id FROM feeds WHERE url=:url''', {'url': self.link}).fetchall()[0][0]
            except sqlite3.IntegrityError as error:
                new_id = conn.cursor().execute('''SELECT id FROM feeds WHERE url=:url''', {'url': self.link}).fetchall()[0][0]
            return new_id
        
        if feed_id==None:
            feed_id = create_feed_in_db(self.link, conn, self.title, self.description)
        else:
            feed_id = create_feed_in_db(self.url, conn, self.title, self.description)
                
        # ������ ���� ������ ��� �����, ���� ��������� ��������
        for item in self.items:
            item.store_to_database(conn, feed_id)
        
        conn.commit()
        conn.close()
        
        
    def load_from_database(self, feed_url):
        conn = sqlite3.connect(database)
        
        feed_id = self.get_feed_id(conn, feed_url)
        
        rss_feed_line = conn.cursor().execute('SELECT url, title, descr FROM feeds WHERE id=:feed_id', {'feed_id': feed_id}).fetchall()
        self.link = rss_feed_line[0][0]
        self.title = rss_feed_line[0][1]
        self.description = rss_feed_line[0][2]
        
        self.items = list()
        for sql_line in conn.cursor().execute('''SELECT url, title, content, upd_date 
                        FROM items WHERE feed_id=:feed_id
                        ORDER BY upd_date ASC''', 
                                                                                                     {'feed_id':feed_id}):
            newItem = RssItem()
            newItem.load_from_database_res_line(sql_line)
            self.items.append(newItem)
        
        conn.close()
    def remove_from_database(self, feed_url):
        conn = sqlite3.connect(database)
        
        feed_id = self.get_feed_id(conn, feed_url)
        
        conn.cursor().execute('DELETE FROM feeds WHERE id=:feed_id', {'feed_id': feed_id})
        conn.cursor().execute('DELETE FROM items WHERE feed_id=:feed_id', {'feed_id': feed_id})
        
        conn.commit()
        conn.close()
    
    def get_feed_id(self, conn, feed_url):
        return conn.cursor().execute('SELECT id FROM feeds WHERE url=:feed_url', {'feed_url': feed_url}).fetchall()[0][0]


    
    
    
    
    