import sqlite3
import string
import random
from simplify2 import *

def get_connection():
	conn = sqlite3.connect("database.db")
	return conn


# creation tables
# For creating a new pool with pool_name along with a new user entry in participants
def create_pool(pool_name, username, email):
	conn = get_connection()
	curr = conn.cursor()
	letters = string.ascii_uppercase
	rlink = pool_name+ ''.join(random.choice(letters) for i in range(5))
	curr.execute("INSERT INTO pots (pot_name,pot_link) VALUES(?,?)",(pool_name,rlink))
	pool_id = curr.lastrowid
	conn.commit()
	conn.close()
	entry_participant(pool_id,username,email)
	return rlink


# Adds a new participant
def entry_participant(poolid,username,email):
	conn = get_connection()
	curr = conn.cursor()
	curr.execute("INSERT INTO participants (pot_id,participant_name,mail,paid,consumed,net) VALUES(?,?,?,?,?,?)",(poolid,username,email,0,0,0))
	conn.commit()
	conn.close()


# getter methods for tables
# returns the pool_id from pool_link
def get_pool_id(pool_link):
	conn = get_connection()
	curr = conn.cursor()
	poolid = curr.execute("SELECT p_id FROM pots WHERE pot_link=?",(pool_link,)).fetchone()
	conn.close()
	if poolid is None:
		return -1
	else:
		return poolid[0]


# returns list of participants in the pool
def get_participants(poolid):
	conn = get_connection()
	curr = conn.cursor()
	query = "SELECT * FROM participants WHERE pot_id = {} ".format(poolid)
	participants = curr.execute(query).fetchall()
	print(participants)
	conn.close()
	return participants


# returns a single participant details
def get_participant(uid):
	conn = get_connection()
	curr = conn.cursor()
	query = "SELECT participant_name,mail FROM participants WHERE uid= {}".format(uid)
	p_details = curr.execute(query).fetchone()
	print(p_details)
	conn.close()
	return p_details


# updates the user details
def update_user(username,mail,uid):
	conn = get_connection()
	curr = conn.cursor()
	query = "UPDATE participants SET participant_name='{uname}', mail='{mail}' WHERE uid={pid}".format(uname = username,mail = mail,pid = uid)
	curr.execute(query)
	conn.commit()
	conn.close()




# returns list of settlement details
def get_settlement(pool_id):
	conn = get_connection()
	curr = conn.cursor()
	query = "SELECT * FROM settlement WHERE pot_id = {}".format(pool_id)
	users = curr.execute(query).fetchall()
	conn.close()
	if users is None:
		return -1
	else:
		return users


# returns list of items
def get_items(pool_id):
	print(pool_id)
	conn = get_connection()
	curr = conn.cursor()
	# query = "SELECT * FROM transactions WHERE pot_id = {}".format(pool_id)
	query = '''SELECT I.t_id,I.pot_id,I.description,I.created,I.amount,I.paidby, COUNT(C.transaction_id) 
    AS count FROM transactions I JOIN consumers C ON I.t_id=C.transaction_id WHERE I.pot_id={} GROUP BY transaction_id'''.format(
		pool_id)
	items = curr.execute(query).fetchall()
	conn.close()
	if items is None:
		return -1
	else:
		print(items)
		return items


# Enter items into db
def entry_item(pool_id, description, date, amount, payer_name, consumer, consumer_amount, expense_type,col2):
    conn = get_connection()
    curr = conn.cursor()
    curr.execute("INSERT INTO transactions (pot_id,description,created,amount,paidby,split) VALUES(?,?,?,?,?,?)",
				 (pool_id, description, date, amount, payer_name,expense_type))
	# query="SELECT t_id FROM transactions WHERE description = {}".format(description)
	# item_id=curr.execute(query).fetchone()
    item_id = curr.lastrowid
    for i in range(len(consumer)):
        curr.execute("INSERT INTO consumers (transaction_id,consumer_name,amount) VALUES(?,?,?)",
					 (item_id, consumer[i], consumer_amount[i]))
        c_id=curr.lastrowid
        if(col2!=-1):
            curr.execute("INSERT INTO col2 (c_id,col2values) VALUES(?,?)",
                         (c_id,col2[i]))
	
    conn.commit()
    conn.close()
    update_participant(pool_id,payer_name,amount,consumer,consumer_amount)
    settlement_simplify(pool_id)


# returns name of all participants
def get_participants_name(pool_id):
	conn = get_connection()
	curr = conn.cursor()
	query = "SELECT participant_name FROM participants WHERE pot_id = {} ".format(pool_id)
	participant_names = curr.execute(query).fetchall()
	print(participant_names)
	conn.close()
	return participant_names


# return single item details
def get_item(item_id):
	conn = get_connection()
	curr = conn.cursor()
	query = "SELECT description,created,amount,paidby,split FROM transactions WHERE t_id= {}".format(item_id)
	query2 = "SELECT consumer_name,amount,c_id FROM consumers WHERE transaction_id={}".format(item_id)
	item = curr.execute(query).fetchone()
	consumers = curr.execute(query2).fetchall()
	#print(item, consumers)
	conn.close()
	return item, consumers


# check if item_id exists or not
def item_exists(item_id):
    conn = get_connection()
    curr = conn.cursor()
    query = "SELECT t_id FROM transactions WHERE t_id={}".format(item_id)
    if (curr.execute(query).fetchone()):
        conn.close()
        return 1
    else:
        conn.close()
        return -1

#returns col2 values(divisons)

def get_coltwo(consumers_ids):
    conn = get_connection()
    curr = conn.cursor()
    col2_values=[]
    for cid in consumers_ids:
        query = "SELECT col2values FROM col2 WHERE c_id={}".format(cid)
        col2_values.append(curr.execute(query).fetchone())
    
    conn.close()
    return col2_values

def update_item(pool_id,item_id, description, date, amount, payer_name, consumer, consumer_amount, expense_type,col2,old_item,old_consumers):
    conn = get_connection()
    curr = conn.cursor()
    query = "SELECT c_id FROM consumers WHERE transaction_id={}".format(item_id)
    consumer_ids = curr.execute(query).fetchall()
    conn.close()
    if col2!=-1:
        for cid in consumer_ids:
            deletecol2(cid[0])
    deleteconsumer(item_id)
    query = "UPDATE transactions SET description='{des}' , created='{dated}' ,amount={money},paidby='{pdby}',split='{exp_type}' WHERE t_id={tid} ".format(des=description,dated=date,money=amount,pdby=payer_name,exp_type=expense_type,tid=item_id)
    conn = get_connection()
    curr = conn.cursor()
    curr.execute(query)
    for i in range(len(consumer)):
        curr.execute("INSERT INTO consumers (transaction_id,consumer_name,amount) VALUES(?,?,?)",
					 (item_id, consumer[i], consumer_amount[i]))
        c_id=curr.lastrowid
        if(col2!=-1):
            curr.execute("INSERT INTO col2 (c_id,col2values) VALUES(?,?)",
                         (c_id,col2[i]))
	
    conn.commit()
    conn.close()
    old_to_new_adjust(pool_id,old_item,old_consumers)
    update_participant(pool_id,payer_name,amount,consumer,consumer_amount)
    settlement_simplify(pool_id)
    
    
def deleteconsumer(t_id):
    conn = get_connection()
    curr = conn.cursor()
    query = "DELETE FROM consumers WHERE transaction_id={}".format(t_id)
    curr.execute(query)
    conn.commit()
    conn.close()
    
def deletecol2(c_id):
    conn = get_connection()
    curr = conn.cursor()
    #query =  "DELETE FROM col2 WHERE c_id={}".format(c_id)
    curr.execute("DELETE FROM col2 WHERE c_id=?",(c_id,))
    conn.commit()
    conn.close()

#update participant paid consumed and net values
def update_participant(pot_id,paidby,amount,consumers,consumer_amount):
	conn = get_connection()
	curr = conn.cursor()
	query = "SELECT paid,consumed FROM participants WHERE pot_id =? and participant_name = ?"
	paid_values = curr.execute(query,(pot_id,paidby,)).fetchone()
	print(type(paid_values),type(amount))
	updated_paid = round(paid_values[0]+float(amount),2)
	updated_net = updated_paid - paid_values[1]
	query1 = "UPDATE participants SET paid = ?,net = ? WHERE pot_id = ? and participant_name = ?"
	curr.execute(query1,(updated_paid,updated_net,pot_id,paidby))

	for i in range(len(consumers)):
		consumed_values = curr.execute(query,(pot_id,consumers[i],)).fetchone()
		print(consumed_values,consumer_amount[i])
		updated_consumed = round(consumed_values[1] + float(consumer_amount[i]),2)
		updated_net = consumed_values[0] - updated_consumed
		query1 = "UPDATE participants SET consumed = ?,net = ? WHERE pot_id = ? and participant_name = ?"
		curr.execute(query1,(updated_consumed,updated_net,pot_id,consumers[i],))

	conn.commit()
	conn.close()

def old_to_new_adjust(pool_id,old_item,old_consumers):
	paidby = old_item[3]
	amount = old_item[2]
	conn = get_connection()
	curr =conn.cursor()
	query = "SELECT paid,consumed FROM participants WHERE pot_id = ? and participant_name = ?"
	old_values = curr.execute(query,(pool_id,paidby,)).fetchone()
	paid_change = round(old_values[0] - float(amount),2)
	net_change = paid_change - old_values[1]
	query1 = "UPDATE participants SET paid = ?,net= ? WHERE pot_id = ? and participant_name = ?"
	curr.execute(query1,(paid_change,net_change,pool_id,paidby))
	for i in range(len(old_consumers)):
		old_cvalues = curr.execute(query,(pool_id,old_consumers[i][0],)).fetchone()
		consumed_change = round(old_cvalues[1] - float(old_consumers[i][1]),2)
		net_change = old_cvalues[0] - consumed_change
		query1 = "UPDATE participants SET consumed = ?,net= ? WHERE pot_id =? and participant_name = ?"
		curr.execute(query1,(consumed_change,net_change,pool_id,old_consumers[i][0],)) 
	conn.commit()
	conn.close()
#for settlement
def settlement_simplify(pool_id):
	conn = get_connection()
	curr = conn.cursor()
	query = "SELECT net FROM participants WHERE pot_id ={}".format(pool_id)
	net_values = curr.execute(query).fetchall()
	query = "SELECT participant_name FROM participants WHERE pot_id={}".format(pool_id)
	participants = curr.execute(query).fetchall()
	print(net_values,participants)
	net = []
	for x in net_values:
		net.append(x[0])
	participant_names = []
	for p in participants:
		participant_names.append(p[0])
        
	balance_sheet = simplify.simplify(net,participant_names)
	print(balance_sheet)
	query = "DELETE FROM settlement WHERE pot_id = ?"
	curr.execute(query,(pool_id,))
	conn.commit()
		
	for receiver in balance_sheet:
		for payer in balance_sheet[receiver]:
			if balance_sheet[receiver][payer] >= 0:	
				#add into sql table
				#add into sql table
				curr.execute("INSERT INTO settlement (pot_id,payee_name,amount,receiver_name) VALUES(?, ?,?,?)",(pool_id,payer,round(balance_sheet[receiver][payer],2),receiver))
	conn.commit()
	conn.close()



if __name__=="__main__":
	# get_participants(2)
	print(get_pool_id("sdfghsd"))


