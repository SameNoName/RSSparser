# -*- coding: utf-8 -*-
import tkinter as tk
import tkinter.ttk as ttk
import feedparser
import psycopg2
from datetime import datetime
import time
from email.utils import parsedate
import threading

def fillDB(myUrl):
    con = psycopg2.connect(dbname='postgres', user='postgres', password='password', host='localhost')
    cur = con.cursor()
    rss = feedparser.parse(myUrl)
    for item in rss['items']:
        sql = ''' INSERT INTO data (title, description, link, date)
        VALUES (%s,%s,%s,%s)'''
        record = (item['title'], item['description'],item['link'],item['published'])
        cur.execute(sql, record)
        con.commit()

def updateDB(myUrl):
    while True:
        time.sleep(10)
        rss = feedparser.parse(myUrl)
        con = psycopg2.connect(dbname='postgres', user='postgres', password='password', host='localhost')
        cur = con.cursor()
        cur.execute('SELECT max(date) FROM data')
        lastTime = cur.fetchall()
        lastTime = lastTime[0][0]
        for item in rss['items']:
            publishedTime = item['published']
            publishedTime = parsedate(publishedTime)
            publishedTime = datetime.fromtimestamp(time.mktime(publishedTime))
            if publishedTime > lastTime:
                sql = """ INSERT INTO data (title, description, link, date)
                VALUES (%s,%s,%s,%s)"""
                record = (item['title'], item['description'],item['link'],item['published'])
                cur.execute(sql, record)
            else:
                break
        con.commit()

def clicked():  
    con = psycopg2.connect(dbname='postgres', user='postgres', password='password', host='localhost')
    cur = con.cursor()
    cur.execute('DROP TABLE IF EXISTS data')
    sql = '''CREATE TABLE data (id SERIAL PRIMARY KEY NOT NULL,
    title TEXT,
    description TEXT,
    link TEXT,
    date TIMESTAMP)'''
    cur.execute(sql)
    con.commit()
    con.close()
    myUrl = txt.get()
    fillDB(myUrl)
    a = threading.Thread(target=updateDB, args = (myUrl,), daemon=True)
    a.start()
    lbl.configure(text = 'Database is added. Program is running.')

def selectAll():
    tree.delete(*tree.get_children())
    conn = psycopg2.connect(dbname='postgres', user='postgres', password='password', host='localhost')
    cur = conn.cursor()
    cur.execute("SELECT title, description, link, date FROM data ORDER BY date DESC")
    for row in cur.fetchall():
        tree.insert('', tk.END, values = row)
        
def select():
    tree.delete(*tree.get_children())
    text = likeTxt.get()
    conn = psycopg2.connect(dbname='postgres', user='postgres', password='password', host='localhost')
    cur = conn.cursor()
    sql = "SELECT title, description, link, date FROM data WHERE title ILIKE '%{f}%' OR description ILIKE '%{f}%' ORDER BY date DESC"
    sql = sql.format(f = text)
    cur.execute(sql)
    for row in cur.fetchall():
        tree.insert('', tk.END, values = row)

window = tk.Tk()
window.title("title")
frame = tk.Frame()
lbl = tk.Label(master=frame, text="Введите URL:")  
lbl.grid(column=0, row=0, padx=5, pady=5)
txt = tk.Entry(master=frame, width = 100)  
txt.grid(column=1, row=0, padx=5, pady=5)
btn = tk.Button(master=frame, text="Запустить программу!", command=clicked)  
btn.grid(column=2, row=0, padx=5, pady=5)
btn1 = tk.Button(master=frame, text="Показать все записи!", command=selectAll)
btn1.grid(column=1, row=1, padx=5, pady=5) 
lbl1 = tk.Label(master=frame, text="Поиск:")  
lbl1.grid(column=0, row=2, padx=5, pady=5)
likeTxt = tk.Entry(master=frame, width=100)
likeTxt.grid(column=1, row=2, padx=5, pady=5)
btn2 = tk.Button(master=frame, text="Поиск", command=select)
btn2.grid(column=2, row=2, padx=5, pady=5)
frame.pack(padx=5, pady=5, anchor = 'w')
frame1 = tk.Frame()
frame1.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
tree = ttk.Treeview(frame1, show="headings", selectmode ='browse', columns=('title', 'description', 'link', 'date'))
tree.heading('title', text='Заголовок') 
tree.heading('description', text='Описание') 
tree.heading('link', text='Ссылка')
tree.heading('date', text='Дата публикации')
tree.column('title', minwidth=0, stretch=0)
tree.column('description', width=1000)
tree.column('link', width=250)
tree.column('date', width=120)
tree.pack(side='left', fill=tk.BOTH, expand=True, padx=5, pady=5)
sb = ttk.Scrollbar(frame1, orient='vertical')
sb.pack(side='right', fill='y')
tree.config(yscrollcommand=sb.set)
sb.config(command=tree.yview)
window.mainloop()