# coding = UTF-8
'''
Created on 31 окт. 2013 г.

@author: Adelier
'''
from tkinter.scrolledtext import ScrolledText
from tkinter import *
from RssFeedImpl import RssFeed, get_feed_urls_list, load_from_xml_into_db
from threading import Thread
import webbrowser

class HyperlinkManager:
# from http://effbot.org/zone/tkinter-text-hyperlink.htm
    def __init__(self, text, url):
    
        self.text = text
        self.url = url
    
        self.text.tag_config("hyper", foreground="blue", underline=1)
    
        self.text.tag_bind("hyper", "<Enter>", self._enter)
        self.text.tag_bind("hyper", "<Leave>", self._leave)
        self.text.tag_bind("hyper", "<Button-1>", self._click)
    
        self.reset()

    def reset(self):
        self.links = {}

    def add(self, action):
        # add an action to the manager.  returns tags to use in
        # associated text widget
        tag = "hyper-%d" % len(self.links)
        self.links[tag] = action
        return "hyper", tag

    def _enter(self, event):
        self.text.config(cursor="hand2")

    def _leave(self, event):
        self.text.config(cursor="")

    def _click(self, event):
        for tag in self.text.tag_names(CURRENT):
            if tag[:6] == "hyper-":
                self.links[tag](self.url)
                return

class RssTkinkerGui:

    def __init__(self):
        self.tk = Tk()
        self.pane = PanedWindow(self.tk, orient=HORIZONTAL, borderwidth=3)
        self.rssContent = ScrolledText(self.tk, ) # Text wrap=WORD
        self.rssContent.insert('0.0', '''
В поле новой ленты:
    ввести ссылку и <Enter> чтобы добавить ленту
В списке: 
    <F5> чтобы одновить
    <Delete> чтобы удалить ''')
        
        self.fr = Frame(self.tk)
        self.newUrlEntry = Entry(self.fr, width=28)
        self.urlsListbox = Listbox(self.fr,selectmode=SINGLE)
    
    def on_urls_listbox_select(self,event):
        feed_url = self.urlsListbox.get(self.urlsListbox.curselection()[0])
        feed = RssFeed()
        feed.load_from_database(feed_url)
        
        self.rssContent.delete('0.0', END)
        for item in feed.items:
            # description & pub_date
            self.rssContent.insert('0.0', '\n' + item.pub_date + '\n\n\t' + item.description + 
                                   '\n_______________________________________\n\n')
            # title with link
            hyperlink = HyperlinkManager(self.rssContent, item.link)
            self.rssContent.insert('0.0', item.title, hyperlink.add(self.link_callback))
            
    def link_callback(self,asd):
        # TODO browser
        print('LINK! ' + asd)
        webbrowser.open(asd)
   
    def on_urls_listbox_delete(self,event):
        feed_url = self.urlsListbox.get(self.urlsListbox.curselection()[0])
        feed = RssFeed()
        feed.remove_from_database(feed_url)
        self.fill_urlsListbox()
        
    def on_urls_listbox_f5(self,event):
        feed_url = self.urlsListbox.get(self.urlsListbox.curselection()[0])
        feed = RssFeed()
        feed.load_from_xml_rss(feed_url)
        feed.store_to_database()
        
        self.on_urls_listbox_select(event)
        
    def add_new_url(self,event):
        newUrl = self.newUrlEntry.get()
        thread = Thread(load_from_xml_into_db(newUrl))
        thread.start()
        self.fill_urlsListbox()
    def fill_urlsListbox(self):
        self.urlsListbox.delete(0, END)
        for url in get_feed_urls_list():
            self.urlsListbox.insert(END, url)
        
    def launch(self):
        self.tk.wm_minsize(width=400, height=100)
        self.tk.title("Adelier's RssFeadReader")
        self.tk.geometry('800x600')
        
        self.pane.pack(side=LEFT, fill=BOTH, expand=TRUE)
        
        
        self.pane.add(self.fr)
        #fr.pack(side=LEFT, fill=Y, expand=TRUE)
            
        self.newUrlEntry.bind("<Return>", self.add_new_url)
        self.newUrlEntry.pack(side=TOP, anchor=W, fill=X)
        
            
        self.urlsListbox.bind('<<ListboxSelect>>', self.on_urls_listbox_select)
        self.urlsListbox.bind('<Delete>', self.on_urls_listbox_delete)
        self.urlsListbox.bind('<F5>', self.on_urls_listbox_f5)
        self.fill_urlsListbox()
        self.urlsListbox.pack(anchor=W, fill=BOTH, expand=TRUE)
        
        self.pane.add(self.rssContent)
         
        self.tk.mainloop()
        
        
        
        
        
        