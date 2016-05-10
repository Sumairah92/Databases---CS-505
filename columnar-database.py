import MySQLdb
from Tkinter import *
import tkMessageBox as msg
import Tkinter as tk
import time

db = MySQLdb.connect("localhost","root","xflow","col")
cursor = db.cursor()


#############################Creating Table###########################
def create():
	def create_check():
		db_name = ec1.get()
		q_string = e2.get()
		rows = q_string.split('*')
		metadata = rows[0].split(';')
		att_len = len(metadata)/2
		if len(metadata)/2 >= 10:
			msg.showerror("Error","No more than 10 columns allowed")
		elif len(rows[1]) == 0:
			msg.showerror("Error","You must enter atleast one row")
		elif not db_name:
			msg.showerror("Error", "You must enter a table name")
		else:
			i = 0
			while i <= len(metadata)-1:
				sql = "create table %s_%s (k INTEGER PRIMARY KEY, %s %s)"%(db_name,metadata[i],metadata[i],metadata[i+1])
				cursor.execute(sql)
#				print sql
				i = i+2
			i = 1
			while i < len(rows):
				data = rows[i].split(';')
				if (len(data) != att_len):
                			msg.showerror("Error","Attribute values cannot be null")
					db.rollback()
					break
				k = 0
				x = 0
				while x <= len(data)-1:
					sql = "insert into %s_%s values(%d,'%s')"%(db_name,metadata[k],i,data[x])
#					print sql
					cursor.execute(sql)
					k = k+2
					x = x+1
				i = i+1
#	db.commit()
	createp = Tk()
	createp.wm_title("Create table")
	L2 = tk.Label(createp,text = "Enter data for table in required format", font="bold")
	L2.pack(side="top",expand=True)
	L3 = tk.Label(createp, text = "Table name")
	L3.pack()
	ec1 = tk.Entry(createp)
	ec1.pack()
	L4 = tk.Label(createp, text = "Table description and data")
	L4.pack()
	e2 = tk.Entry(createp)
	e2.pack(fill = BOTH, expand = 1)
	B1 = tk.Button(createp, text = "Create", command = create_check)
	B2 = tk.Button(createp, text = "Quit", command = createp.destroy)
	B1.pack()
	B2.pack()

##########################################################################

############################Querying tables#############################
def query():
	def showresult():
		res = Tk()
        	res.wm_title("Query Result")
        	R = Listbox(res)
		row = cursor.fetchone()
		if row is None:
			msg.showerror("Error","No data was returned")
		else:
			while row is not None:
				result = ''
				x = 1
				result = str(row[0])
				while x < len(row):
					result = result + "," + str(row[x]) 
					x = x+1
					print result
				R.insert(END,'%s'%result)
				row = cursor.fetchone()
			R.pack(fill=BOTH,expand=True)
        		B1 = tk.Button(res, text = "Quit", command = res.destroy)
 	      		B1.pack()
		
	def querycheck():
		q_string = e1.get()
		rows = q_string.split()
		i = rows.index('FROM')
		db_name = rows[i+1]
		cols = rows[i-1].split(',')
		num_col = len(cols);
		k = 1
		sql = "SELECT "
		while k <= num_col:
			sql = sql + "t%d.%s"%(k,cols[k-1])
			if k != num_col:
				sql = sql + "," 
			k = k+1
		sql = sql + " "
		sql = sql + "FROM "
		k = 1
		while k <= num_col:
			sql = sql + "%s_%s AS t%d"%(db_name,cols[k-1],k)
			if k != num_col:
				sql = sql + ","
			k = k+1
	
		i = rows.index('WHERE')
		while i <= len(rows)-1:
			k = 1
			while k <= num_col:
				if(rows[i] == cols[k-1]):
					rows[i] = "t%d.%s"%(k,cols[k-1])
				k = k+1
			sql = sql + " "
			sql = sql + rows[i]
			i = i+1
		k = 1	
		while k+1 <= num_col:
			sql = sql + " AND "
			sql = sql + "t%d.k = t%d.k "%(k,k+1)
			k = k+1
		msg.showinfo("Transformed Query","%s"%(sql))
		cursor.execute(sql)
		showresult()	
	queryp = Tk()
	queryp.wm_title("Query table")
	L2 = tk.Label(queryp,text = "Enter Query", font="bold")
	L2.pack(side="top",expand=True)
	e1 = tk.Entry(queryp)
	e1.pack(fill=BOTH, expand = 1)
	B1 = tk.Button(queryp, text = "Run", command = querycheck)
	B2 = tk.Button(queryp, text = "Quit", command = queryp.destroy)
	B1.pack()
	B2.pack()


################################UI################################


root = Tk()
root.title("Welcome to Main window")
frame = Frame(root)
frame.pack()
L1 = Label(frame, text="Please select an action", font = "bold")
L1.pack()
B1 = Button(frame, text = "Create table and insert data", command = create, activebackground = 'white')
B2 = Button(frame, text = "Query a table", command = query, activebackground="white")
B3 = Button(frame, text = "Close", command = root.quit,activebackground="white")
B1.pack()
B2.pack()
B3.pack()
root.mainloop()

