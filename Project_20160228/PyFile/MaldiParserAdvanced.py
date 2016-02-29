#MALDI Parser Advanced

## Import Modules
import xlrd
import pandas as pd
import numpy as np
import warnings
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import threading

## Helper Functions

### Finding missed peak(s) 

#Finding Missed Peak
def detect_missed(mzs):
    global normal_mzs
    mzs_missing=[]
    
    for normal_mz in normal_mzs:
        for mz in mzs:
            if mz<normal_mz+6 and mz>normal_mz-6:   #Searching in this range
                break
        else:
            mzs_missing.append(normal_mz)
    return mzs_missing

### Finding redundant peak(s)

#Finding Redundant Peak
def detect_redundant(mzs):
    mzs_adjacents=[]    

    for normal_mz in normal_mzs:
        d=9.99
        m=0
        for mz in mzs:
            if abs(normal_mz-mz)<d:
                d=abs(normal_mz-mz)
                m=mz
        mzs_adjacents.append(m)
   
    return mzs_adjacents

### Display the layout

#Layout Display
def layout(names):
    layout_names=[]
    layout_series=[]
    for name in names:
        patt4=r'[\D\d]+_0_'
        sample_name=re.findall(patt4, name)[0].replace('_0_', '').replace('-', '_')
        
        if sample_name.find('standard')!=-1 or sample_name.find('Standard')!=-1:
            sample_name=sample_name.replace('standard', '').replace('Standard', '').replace('_', '')       

        patt5=r'_0_[\D\d]+_1$'
        id_name=re.findall(patt5, name)[0].replace('_0_', '').replace('_1', '')

        if len(id_name)==2:
            id_name=id_name[0]+'0'+id_name[1]

         
        layout_names.append((id_name, sample_name))

    d=96-len(layout_names)

    for i in range(d):
        layout_names.append(('Z'+str(i),np.nan))

    sample_dict=dict(layout_names)
    s=pd.Series(sample_dict).sort_index()
    df=pd.DataFrame(np.array(s).reshape(8,12),
                           columns=[1,2,3,4,5,6,7,8,9,10,11,12],
                           index=['A','B','C','D','E','F','G','H'])
    return df

### Browse File

def browseFileButton():
    global filename, indicator_progress
    try:
        filename = filedialog.askopenfilename(filetypes=(('Excel files', '*.xlsx'), ('All files', '*.*')))
        
        text_filename.delete('1.0', tk.END)
        text_filename.insert('1.0', filename)
        
        indicator_process = 0
        progressbar['value'] = indicator_process
        
    except:
        filename = ''

### Process Data Munging

def process():
    global filename, df, normal_mzs, indicator_process
    
    if filename == '':
        messagebox.showwarning("No File", "Sorry, no file loaded! Please choose Excel file first.")
    else:
        #Ignoring Warnings
        warnings.filterwarnings("ignore")
        
        indicator_process = 0

        #Default Peaks
        peak01 = int(text_peak01.get('1.0', tk.END))
        peak02 = int(text_peak02.get('1.0', tk.END))
        
        normal_mzs=[peak01, peak02]
        normal_rows=len(normal_mzs)

        #Import File
        book=xlrd.open_workbook(filename)
        #print('Source file: '+sys.path[0]+filename+' loaded!')

        #Extraction
        nsheets=book.nsheets

        sheet_names=book.sheet_names()
        sheets={}

        for sheet_name in sheet_names:    
            nrows=book.sheet_by_name(sheet_name).nrows
            current_header=book.sheet_by_name(sheet_name).row_values(2) 
            current_data=[book.sheet_by_name(sheet_name).row_values(i) for i in range(3, nrows)]
            sheets[sheet_name]=pd.DataFrame(current_data, columns=current_header)   #DataFrame Construction
        #Feedback
        #print('Data Extracted!')
        #Dealing with the Missing Peak(s)
        #///////////////////Main Loop///////////
        peak_missing_amount=0
        peak_redundant_amount=0
        peak_redundant_item=[]
        peak_missing_item=[]
        peak_repeated_amount=0
        peak_repeated_item=[]
        
        gain = 1000/len(sheet_names)

        for sheet_name in sheet_names:
            df=sheets[sheet_name]

            actual_rows=len(df.index)
            mzs=list(df['m/z'])

            #////////////////////Unique!!!!///////////////////////////////////////////////
            for mz in mzs:
                if len(df[df['m/z']==mz].index)>1:
                    del_index=list(df[df['m/z']==mz].index)
                    del_index.pop(0)
                    df=df.drop(del_index)

                    mzs=list(df['m/z'])

                    peak_repeated_amount+=1
                    peak_repeated_item.append(sheet_name.replace('_0_', ' @ ').replace('_1', ''))
            #////////////////////////////////////////////////////////////////////////////

            df=df.sort_index(by='m/z')
            df=df.reset_index().drop('index', axis=1)

            actual_rows=len(df.index)

            #///////Larger than normal: Redundant///////////
            if actual_rows>normal_rows:
                mzs=list(df['m/z'])
                mzs_adjacents=detect_redundant(mzs)    #Call Function          
                df=pd.concat([df.ix[df[df['m/z']==mzs_adjacent].index] for mzs_adjacent in mzs_adjacents])        

                #////Memorize the Redundant One//////////////////    
                peak_redundant_amount+=1
                peak_redundant_item.append(sheet_name.replace('_0_', ' @ ').replace('_1', ''))

            #/////Sort & Reindex////////////
            df=df.sort_index(by='m/z')
            df=df.reset_index().drop('index', axis=1)

            actual_rows=len(df.index)

            ##///////Less than normal: Missing///////
            if actual_rows<normal_rows:
                mzs=list(df['m/z'])
                mzs_missing=detect_missed(mzs)  #Call Function 

                i=actual_rows

                for mz_missing in mzs_missing:
                    df.ix[i]=0
                    df['m/z'].ix[i]=mz_missing
                    i+=1

                #////Memorize the Missing One///////
                peak_missing_amount+=1
                peak_missing_item.append(sheet_name.replace('_0_', ' @ ').replace('_1', ''))

            df=df.sort_index(by='m/z')
            df=df.reset_index().drop('index', axis=1)

            actual_rows=len(df.index)    

            #///////Again! Larger than normal: Redundant////////
            if actual_rows>normal_rows:
                mzs=list(df['m/z'])
                mzs_adjacents=detect_redundant(mzs)     #Call Function          
                df=pd.concat([df.ix[df[df['m/z']==mzs_adjacent].index] for mzs_adjacent in mzs_adjacents])       

                #/Memorize the Redundant One
                peak_redundant_amount+=1
                peak_redundant_item.append(sheet_name.replace('_0_', ' @ ').replace('_1', ''))

            #Sort & Reindex/////////////
            df=df.sort_index(by='m/z')
            df=df.reset_index().drop('index', axis=1)     

            sheets[sheet_name]=df
            
            indicator_process += gain

        df=pd.concat([sheets[sheet_name] for sheet_name in sheet_names], keys=sheet_names)

        #///Change the sheetnames from indeces into column names
        df=df.reset_index()

        #Sorting
        df = df.sort_index(by=['level_0', 'level_1'])
        df = df.set_index(['level_0', 'level_1'])
        df = df.unstack()
       

def start_process_thread(event):
    global process_thread, indicator_process
    process_thread = threading.Thread(target=process)
    process_thread.daemon = True
    
    progressbar['value'] = indicator_process
    
    process_thread.start()
    root.after(20, check_process_thread)

def check_process_thread():
    if process_thread.is_alive():
        progressbar['value'] = indicator_process
        
        root.after(20, check_process_thread)
    else:
        messagebox.showinfo("Data Processed", "Data successfully processed!")

### Export File

def exportFileButton():
    directory = filedialog.askdirectory()
    if filename == '':
        messagebox.showwarning("No File to be Exported", "Sorry, no file to be exported! Please choose a Excel file first.")
    elif directory == '':
        messagebox.showwarning("No Directory", "Sorry, no directory shown! Please specify the output directory.")
    else:
        filename_output = directory + '/' + filename.split('.')[0].split('/')[-1] + '.csv'
        df.to_csv(filename_output)
        messagebox.showinfo("File Exported", "File successfully exported!")

### Main Program Flow

#### We chose 2 peaks for detection: **2791, 2819** (Hepcidin)

# Main Frame////////////////////////////////////////////////////////////////////////////////////////
root = tk.Tk()

peak01 = 2791
peak02 = 2819
indicator_process = 0

filename = ''

w = 700 # width for the Tk root
h = 500 # height for the Tk root

# get screen width and height
ws = root.winfo_screenwidth() # width of the screen
hs = root.winfo_screenheight() # height of the screen

# calculate x and y coordinates for the Tk root window
x = (ws/2) - (w/2)
y = (hs/2) - (h/2)

# set the dimensions of the screen 
# and where it is placed
root.geometry('%dx%d+%d+%d' % (w, h, x, y))
#root.attributes('-fullscreen', True)
root.title('MALDI Parser')

# Progress Bar
progressbar = ttk.Progressbar(root, length=500, maximum=1000, mode='determinate')
progressbar.place(x=60,y=250)

# Text
text_filename=tk.Text(root, width=80,height=1, font=('tahoma', 9), bd=2)
text_filename.place(x=60, y=50)
label_filename=tk.Label(root, text='Import Excel File:', font=('tahoma', 9))
label_filename.place(x=60,y=20)

text_peak01=tk.Text(root, width=8,height=1, font=('tahoma', 9), bd=2)
text_peak01.place(x=130, y=190)
label_peak01=tk.Label(root, text='Peak 01:', font=('tahoma', 9))
label_peak01.place(x=60,y=190)
text_peak01.delete('1.0', tk.END)
text_peak01.insert('1.0', str(peak01))

text_peak02=tk.Text(root, width=8,height=1, font=('tahoma', 9), bd=2)
text_peak02.place(x=330, y=190)
label_peak02=tk.Label(root, text='Peak 02:', font=('tahoma', 9))
label_peak02.place(x=260,y=190)
text_peak02.delete('1.0', tk.END)
text_peak02.insert('1.0', str(peak02))


# Buttons
button_browse=ttk.Button(root, text='Browse...', width=20, command=browseFileButton)
button_browse.place(x=60, y=110)

button_process=ttk.Button(root, text='Process', width=20, command=lambda:start_process_thread(None))
button_process.place(x=60, y=310)

button_browse=ttk.Button(root, text='Export', width=20, command=exportFileButton)
button_browse.place(x=60, y=410)

button_close=ttk.Button(root, width=20, text='Exit', command=root.destroy)
button_close.place(x=450, y=410)

root.mainloop()