#written by: Shamim,Sumaira
#!/usr/bin/python

import MySQLdb 
from Tkinter import * 
import tkMessageBox as msg
import Tkinter as tk
import time

db = MySQLdb.connect("localhost","root","xflow","MSM")
cursor = db.cursor()
cursor_p = db.cursor()
cursor_f = db.cursor()

#########################################################3
def now():
	stamp = time.strftime('%Y-%m-%d %H:%M:%S')
	return stamp

def refresh_login():
	e1.delete(0,END)
	e2.delete(0,END)

def authenticate():
	global Cur_user
	Cur_user = e1.get()
	Cur_pass = e2.get()
	current = Cur_user
        cursor.execute('select user_id from login where user_id = %s and password = %s',(Cur_user, Cur_pass))
        row = cursor.fetchone()
        if row is not None:
		if Cur_user == 'SO':
			cursor.execute('Insert into Logs VALUES(NULL,"Login",%s,%s)',(Cur_user,now()))
			db.commit()
			msg.showinfo("Login successful","Welcome Security officer")
			root.withdraw()
			seo.deiconify()
		else:
			cursor.execute('Insert into Logs VALUES(NULL,"Login",%s,%s)',(Cur_user,now()))
                        db.commit()
       			msg.showinfo("Login successful","welcome user %s"%(Cur_user))
			root.withdraw()
			userp.deiconify()
        else:
                msg.showerror("Login error","Incorrect username or password")
		refresh_login()
###############################################################

def grant_permission():
	def clear(event=None):
		e1.delete(0,END)
		e2.delete(0,END)
		e3.delete(0,END)
	def stop_prog(event=None):
		userp.deiconify()
		grant.destroy()
	def check_grant(event=None):
		username=e1.get()
		tablename=e2.get()
		grantbit=e3.get()
		grantbit=int(grantbit)
		cursor.execute('Insert into Logs VALUES(NULL,"Update: Grant access on %s to %s",%s,%s)',(tablename,username,Cur_user,now()))
		db.commit()
		if username == Cur_user:
			cursor.execute('Insert into Logs VALUES(NULL,"Rollback: Grant access on %s to %s",%s,%s)',(tablename,username,Cur_user,now()))
			db.commit()
			msg.showerror("Forbidden","You cannot issue permission for yourself")
			clear()
		else:
			cursor_p.execute('select * from permitted where user_name = %s and table_name = %s',(Cur_user, tablename))
			cursor_f.execute('select * from forbidden where user_name = %s and table_name = %s',(username, tablename))

		        row = cursor_p.fetchone()
			row2 = cursor_f.fetchone()
			if row is None or row[3] == 0:
				msg.showerror("Forbidden","You Donot have the permission to grant access to this table.")
				cursor.execute('Insert into Logs VALUES(NULL,"Rollback: No permission to grant access to table %s",%s,%s)',(tablename,Cur_user,now()))
				cursor.execute('Insert into Logs VALUES(NULL,"Forbidden: %s tried to grant permission to user %s to access table %s","SO",%s)',(Cur_user,username,tablename,now()))
				db.commit()
				clear()
			elif row2 is not None:
				cursor.execute('Insert into Logs VALUES(NULL,"Rollback: User %s has no permission to access table %s",%s,%s)',(username,tablename,Cur_user,now()))
                                db.commit()
				msg.showerror("Forbidden", "Grantee is on forbidden list")
				clear()
			else:
				cursor_p.execute('select * from permitted where user_name = %s and table_name = %s',(username, tablename))
				row3 = cursor_p.fetchone()
				if row3 is not None:
					cursor.execute('Insert into permitted VALUES(NULL,%s,%s,%s)',(username, tablename,grantbit))
					msg.showinfo("Success","Permission was successfully granted")
					db.commit()
					cursor.execute('Delete from permitted where id = %s',(int(row3[0])))
				clear()
				db.commit()
							
	grant = Tk()
	grant.title("Grant access values")
	Label(grant, text="User Name").grid(row=0)
	Label(grant, text="Table Name").grid(row=1)
	Label(grant, text="Delegate").grid(row=2)
	e1= Entry(grant)
	e2= Entry(grant)
	e3= Entry(grant)
	e1.grid(row = 0, column = 1)
	e2.grid(row = 1, column = 1)
	e3.grid(row = 2, column = 1)

	Button(grant, text = "Go back", command = stop_prog).grid(row = 3, column = 0)
	Button(grant, text = "Grant", command = check_grant).grid(row = 3,column = 1)
#########################################################

def request_access():
        def stop_prog(event=None):
                userp.deiconify()
                request.destroy()
        def check_request(event=None):
                tablename=e1.get()
		cursor.execute('Insert into Logs VALUES(NULL,"Update: Request access to %s",%s,%s)',(tablename,Cur_user,now()))
		db.commit()
                cursor_p.execute('select * from permitted where user_name = %s and table_name = %s',(Cur_user, tablename))
                cursor_f.execute('select * from forbidden where user_name = %s and table_name = %s',(Cur_user, tablename))

                row = cursor_p.fetchone()
                row2 = cursor_f.fetchone()
                if row is not None:
                	msg.showerror("Error","You already have permission to access this table")
			cursor.execute('Insert into Logs VALUES(NULL,"Rollback: Request access to %s",%s,%s)',(tablename,Cur_user,now()))
			db.commit()
			e1.delete(0,END)
                elif row2 is not None:
			cursor.execute('Insert into Logs VALUES(NULL,"Rollback: Request access to %s",%s,%s)',(tablename,Cur_user,now()))
			cursor.execute('Insert into Logs VALUES(NULL,"Forbidden: %s tried to request access to table %s","SO",%s)',(Cur_user,tablename,now()))
                        db.commit()
                        msg.showerror("Error", " Your access is forbidden for this table")
			e1.delete(0,END)
                else:
                        cursor.execute('Insert into permitted VALUES(NULL,%s,%s,1)',(Cur_user, tablename))
                        msg.showinfo("Success","Your request for access has been approved")
                        db.commit()
			e1.delete(0,END)


        request = Tk()
        request.title("Request access to")
	Label(request, text="Table Name").grid(row=0)
        e1= Entry(request)
        e1.grid(row = 0, column = 1)

        Button(request, text = "Go back", command = stop_prog).grid(row = 3, column = 0)
        Button(request, text = "Request", command = check_request).grid(row = 3,column = 1)

#########################################################################
def view_logs():
	logs = Tk()
	logs.wm_title("Logs")
	scrollbar = Scrollbar(logs)
	scrollbar.pack(side=RIGHT, fill = Y)
	mylogs = Listbox(logs,yscrollcommand = scrollbar.set,width=100,height=20)
	cursor.execute('select * from Logs where user_name = %s',(Cur_user))
	row = cursor.fetchone()
	x=0
	while row is not None:
        	x = x+1
        	mylogs.insert(END,'%d <%s,%s,%s>'%(x,row[1],row[2],row[3]))
        	row = cursor.fetchone()
	mylogs.pack(side = LEFT,fill ="both", expand = True)
	scrollbar.config(command = mylogs.yview)
	b1= Button(logs, text = "Exit", command = logs.destroy)
	b1.pack(side=BOTTOM)


#####################################################################
def forbid_entry():
        def stop_prog(event=None):
                seo.deiconify()
                forbid.destroy()
        def check_forbid(event=None):
		username=e1.get()
                tablename=e2.get()
                cursor_p.execute('select * from permitted where user_name = %s and table_name = %s',(username, tablename))
                cursor_f.execute('select * from forbidden where user_name = %s and table_name = %s',(username, tablename))
		cursor.execute('Insert into Logs VALUES(NULL,"Update: Forbid access to table %s to user %s","SO",%s)',(tablename,username,now()))
		db.commit()
                row = cursor_p.fetchone()
                row2 = cursor_f.fetchone()
                if row2 is not None:
			cursor.execute('Insert into Logs VALUES(NULL,"Rollback: Forbid access to table %s to user %s. Forbidden entry already exists","SO",%s)',(tablename,username,now()))
			db.commit()
                        msg.showerror("Error","You already have forbidden this table to this user")
			e1.delete(0,END)
			e2.delete(0,END)
                elif row is not None:
			cursor.execute('Insert into Logs VALUES(NULL,"Rollback: Forbid access to table %s to user %s. Entry exists in permitted table","SO",%s)',(tablename,username,now()))
			db.commit()
                        msg.showerror("Illegal Operation", " This user is already permitted for this table")
			e1.delete(0,END)		
			e2.delete(0,END)
                else:
                        cursor.execute('Insert into forbidden VALUES(NULL,%s,%s)',(username, tablename))
                        msg.showinfo("Success","Entry was successful")
                        db.commit()
			e1.delete(0,END)
			e2.delete(0,END)

        forbid = Tk()
        forbid.title("Forbid access values")
	Label(forbid, text="User Name").grid(row=1,sticky=E,columnspan=2)
	Label(forbid, text="Table Name").grid(row=2,sticky=E,columnspan=2)
        e1= Entry(forbid)
	e2= Entry(forbid)
        e1.grid(row = 1, column=3,columnspan=2)
	e2.grid(row = 2, column=3,columnspan=2)

        Button(forbid, text = "Go back", command = stop_prog).grid(row = 4, column = 2)
        Button(forbid, text = "Forbid", command = check_forbid).grid(row = 4,column = 3)
########################################################################

def delete_entry():
        def stop_prog(event=None):
                seo.deiconify()
                delete.destroy()
        def check_delete(event=None):
                username=e1.get()
                tablename=e2.get()
		cursor.execute('Insert into Logs VALUES(NULL,"Update: Delete forbidden entry for %s to user %s","SO",%s)',(tablename,username,now()))
		db.commit()
                cursor_f.execute('select * from forbidden where user_name = %s and table_name = %s',(username, tablename))

                row2 = cursor_f.fetchone()
                if row2 is None:
			cursor.execute('Insert into Logs VALUES(NULL,"Rollback: Delete forbidden entry for %s to user %s. No entry found","SO",%s)',(tablename,username,now()))
			db.commit()
                        msg.showerror("Error","No such entry found")
			e1.delete(0,END)
			e2.delete(0,END)
                else:
                        cursor.execute('Delete from forbidden where user_name = %s and table_name = %s',(username, tablename))
                        msg.showinfo("Success","Entry deleted")
                        db.commit()
			e1.delete(0,END)
			e2.delete(0,END)

        delete = Tk()
	delete.title("Delete entry values")

	Label(delete, text="User Name").grid(row=1)
        Label(delete, text="Table Name").grid(row=2)
        e1= Entry(delete)
        e2= Entry(delete)
        e1.grid(row = 1, column = 1)
        e2.grid(row = 2, column = 1)

        Button(delete, text = "Go back", command = stop_prog).grid(row = 3, column = 0)
        Button(delete, text = "Delete", command = check_delete).grid(row = 3,column = 1)


###################Graphical User Interface main windows#################
root = Tk()
root.title("Welcome to MSM")
frame = Frame(root)
frame.pack()
Label(frame, text="Please Enter your login details",justify=CENTER).grid(row=0,column=1)
Label(frame, text="User Name").grid(row=1,column=0)
Label(frame, text="Password").grid(row=2,column=0)

e1= Entry(frame)
e2= Entry(frame,show="*")
e1.grid(row = 1, column = 1)
e2.grid(row = 2, column = 1)

Button(frame, text = "Close", command = root.quit, width=14,padx=2).grid(row = 5, column = 0)
Button(frame, text = "Login", command = authenticate, width=14).grid(row = 5,column = 1)

####################################################
def actionSO(event):
	w = event.widget
        index =  int(w.curselection()[0])
        if index == 0:
                seo.withdraw()
                forbid_entry()
        elif index == 1:
                seo.withdraw()
                delete_entry()
        elif index == 2:
                view_logs()

def actionUser(event):
        w = event.widget
        index =  int(w.curselection()[0])
	if index == 0:
		userp.withdraw()
		grant_permission()
	elif index == 1:
		userp.withdraw()
		request_access()
	elif index == 2:
		view_logs()
##################################################
seo = Tk()
seo.wm_title("Security Officer Menu")
seo.geometry('250x200')
L1 = tk.Label(seo,text = "Please choose an option",font="bold")
L1.pack(side="top",expand=True)
options = Listbox(seo,relief=RAISED,bg="white", borderwidth=1)
options.insert(1, " 1. Add to forbidden list")
options.insert(2, " 2. Delete from forbidden list")
options.insert(3, " 3. View your logs")
options.bind('<<ListboxSelect>>',actionSO)
options.pack(side=LEFT,expand=True,fill="both")
B1 = tk.Button(seo, text = "Log off", command = seo.quit)
B1.pack()
seo.withdraw()
###################################################
userp = Tk()
userp.wm_title("User Menu")
L2 = tk.Label(userp,text = "Please choose an option", font="bold")
L2.pack(side="top",expand=True)
Uoptions = Listbox(userp,relief=RAISED)
Uoptions.insert(1, " 1. Grant a permission")
Uoptions.insert(2, " 2. Request access")
Uoptions.insert(3, " 3. View your logs")
Uoptions.bind('<<ListboxSelect>>',actionUser)
Uoptions.pack(side=LEFT,expand=YES,fill="both")
B2 = tk.Button(userp, text = "Log off", command = userp.quit)
B2.pack()
userp.withdraw()

root.mainloop()
db.close()
