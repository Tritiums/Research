#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import yfinance as yf

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import tkinter.font as tkf


# In[2]:


def display_in_table(prices):
        
    for index, price in prices.iterrows():
        line = []
        price_str_list = []
        
        for item in list(price):
            price_str_list.append(str(item))
            
        line.append(str(index))
        line.extend(price_str_list)
        #print(line)
        
        table.insert("", "end", values=line)
        
    '''
    
    #l_test = [['a', 1,2,3,4,5,6,7,8],['b', 9,1,2,3,4,5,6,7]]
    l_test = ['a', 1,2,3,4,5,6,7]
    
    table.insert('', 'end', values=l_test)
    '''


# In[3]:


def clear():
    for i in table.get_children():
        table.delete(i)


# In[4]:


def extract():
    try:
        global stock_df, stock, startTime, endTime

        stock = text_stockName.get('1.0', tk.END).rstrip().upper()
        startTime = text_startTime.get('1.0', tk.END).rstrip()
        endTime = text_endTime.get('1.0', tk.END).rstrip()

        stock_df = yf.download(stock, start=startTime, end=endTime, progress=False)

        clear()
        display_in_table(stock_df)

        #print(stock_df)
        #print(startTime)
    except:
        messagebox.showwarning("Connection Error", "Sorry, connection error. Please try again later.")


# In[5]:


def OnDoubleClick(event):
    global idglb
    try:
        item = table.selection()[0]
        value = table.item(item, 'values')
        iden = value[0]    
        #extractID(iden)
        idglb = iden
    except:
        pass


# In[6]:


def export():
    stock_df.to_csv('ExportFile_' + stock + '_' + startTime + '_' + endTime + '.csv')
    messagebox.showinfo("Export", stock + " price informat successfully exported!")


# In[7]:


def about():
    messagebox.showinfo("About", "Author & Coder: Chuan Yang")


# In[8]:


# Main Frame////////////////////////////////////////////////////////////////////////////////////////
root = tk.Tk()

w = 949 # width for the Tk root
h = 640 # height for the Tk root

# get screen width and height
ws = root.winfo_screenwidth() # width of the screen
hs = root.winfo_screenheight() # height of the screen

# calculate x and y coordinates for the Tk root window
x = (ws/2) - (w/2)
y = (hs/4) - (h/4)

# set the dimensions of the screen 
# and where it is placed
root.geometry('%dx%d+%d+%d' % (w, h, x, y))
#root.attributes('-fullscreen', True)
root.title('Stock Extractor')


# Multicolumn Listbox/////////////////////////////////////////////////////////////////////////////
headers = ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']

table = ttk.Treeview(height="20", columns=headers, selectmode="extended")
table.pack(padx=10, pady=20, ipadx=1200, ipady=190)

i = 1

header_width = [100, 90, 90, 90, 90, 90, 50]
for header in headers:
    table.heading('#'+str(i), text=header.title(), anchor=tk.W, command=lambda c=header: sortby(table, c, 0))
    table.column('#'+str(i), stretch=tk.NO, minwidth=0, width=tkf.Font().measure(header.title())+header_width[i-1])
    i+=1    
table.column('#0', stretch=tk.NO, minwidth=0, width=0)

table.bind("<Double-1>", OnDoubleClick)
#///////////////////////////////////////////////////////////////////////////////////////////

# Scrollbar////////////////////////////////////////////////////////////////////////////////////////
vsb = ttk.Scrollbar(table, orient = "vertical",  command = table.yview)
hsb = ttk.Scrollbar(table, orient = "horizontal", command = table.xview)
## Link scrollbars activation to top-level object
table.configure(yscrollcommand = vsb.set, xscrollcommand = hsb.set)
## Link scrollbar also to every columns
map(lambda col: col.configure(yscrollcommand = vsb.set, xscrollcommand = hsb.set), table)
vsb.pack(side = tk.RIGHT, fill = tk.Y)
hsb.pack(side = tk.BOTTOM, fill = tk.X) 

# Other Controls ///////////////////////////////

text_stockName=tk.Text(root, width=15,height=1, font=('tahoma', 9), bd=1)
text_stockName.place(x=150, y=480)
label_stockName=tk.Label(root, text='Stock Name:', font=('tahoma', 9))
label_stockName.place(x=60,y=480)
text_stockName.delete('1.0', tk.END)
text_stockName.insert('1.0', 'TSLA')

# ///////

text_startTime=tk.Text(root, width=20,height=1, font=('tahoma', 9), bd=1)
text_startTime.place(x=440, y=480)
label_startTime=tk.Label(root, text='Start:', font=('tahoma', 9))
label_startTime.place(x=380,y=480)
text_startTime.delete('1.0', tk.END)
text_startTime.insert('1.0', '2020-01-01')

text_endTime=tk.Text(root, width=20,height=1, font=('tahoma', 9), bd=1)
text_endTime.place(x=740, y=480)
label_endTime=tk.Label(root, text='End:', font=('tahoma', 9))
label_endTime.place(x=680,y=480)
text_endTime.delete('1.0', tk.END)
text_endTime.insert('1.0', '2020-04-30')

# Bottons

button_extract=ttk.Button(root, text='Extract', width=20, command=extract)
button_extract.place(x=60, y=560)

button_export=ttk.Button(root, text='Export to File', width=25, command=export)
button_export.place(x=260, y=560)

button_about=ttk.Button(root, text='About...', width=20, command=about)
button_about.place(x=560, y=560)

button_close=ttk.Button(root, text='Exit', width=20, command=root.destroy)
button_close.place(x=760, y=560)

root.mainloop()

