from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort
from flask_mail import Mail, Message
from helper_db import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key 1234567890 abcd 0987654321'

app.debug = True

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'kalavenakarthik@gmail.com'
app.config['MAIL_PASSWORD'] = 'kjkufxfcjgepugac'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)


# home route
@app.route('/')
def hello():
    return render_template("home1.html")


# user account and pool creation
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        poolname = request.form['poolname']
        plink = create_pool(poolname, username, email)
        msg = Message('Your potid link', sender='sahaja.puligadda@gmail.com', recipients=[email])
        msg.body = 'Hi there! This is your pool id. ' + plink
        mail.send(msg)
        flash("Email is sent your registered mail ID")
        return redirect('/')

    return render_template("create.html")


# Opening a pool site
@app.route('/<pool_link>/participants/')
def pool_dashboard(pool_link):
    pool_id = get_pool_id(pool_link)
    if pool_id != -1:
        participants = get_participants(pool_id)
        return render_template("participants.html", participants=participants, pool_link=pool_link)
    # then update the data and render the template

    else:
        abort(404)
    # Render a error site saying requested url or pool doesn't exist.


# For editing a pre existing user details
@app.route('/<pool_link>/participants/edit/<int:uid>', methods=('GET', 'POST'))
def edit_participant(pool_link, uid):
    pool_id = get_pool_id(pool_link)
    participant = get_participant(uid)

    if request.method == "POST":
        username = request.form.get("name")
        mail = request.form.get('email')
        if username is not None and mail is not None:
            update_user(username, mail, uid)
        return redirect(url_for("pool_dashboard", pool_link=pool_link))

    return render_template('pedit.html', participant=participant, pool_link=pool_link)


# For creating a new User
@app.route('/<pool_link>/participants/new/', methods=('GET', 'POST'))
def add_participant(pool_link):
    pool_id = get_pool_id(pool_link)

    if request.method == "POST":
        action = request.form.get('submit-btn')
        print(action)

        # save the details
        username = request.form.get('username')
        mail = request.form.get('email')
        entry_participant(pool_id, username, mail)

        # now check if user wants to return or add another participant
        if action == 'save':
            return redirect(url_for("pool_dashboard", pool_link=pool_link))
        elif action == 'add-another':
            return redirect(url_for('add_participant', pool_link=pool_link))

    return render_template('pcreate.html', pool_link=pool_link)


# settlement
@app.route('/<pool_link>/settlement/')
def pool_settlement(pool_link):
    pool_id = get_pool_id(pool_link)

    if pool_id != -1:
        settlement = get_settlement(pool_id)
        print(settlement)
        return render_template('settlement.html', settlement=settlement, pool_link=pool_link)
    else:
        abort(404)


# display_items
@app.route('/<pool_link>/items/')
def pool_items(pool_link):
    pool_id = get_pool_id(pool_link)

    if pool_id != -1:
        items = get_items(pool_id)
        return render_template('items.html', items=items, pool_link=pool_link)
    else:
        abort(404)


# add_item
@app.route('/<pool_link>/items/new/', methods=('GET', 'POST'))
def add_item(pool_link):
    pool_id = get_pool_id(pool_link)
    participants =list(get_participants_name(pool_id))
    #print(participants)
    for partcipant in participants:
        print(partcipant[0])
    if request.method == "POST":
        # save the details
        action = request.form.get('submit-btn')
        description = request.form.get('description')
        date = request.form.get('today_date')
        amount = request.form.get('amount')
        payer_name = request.form.getlist('payerName')
        consumer = request.form.getlist('consumer_name')
        consumer_amount = request.form.getlist('consumer_amount')
        print(consumer,consumer_amount)
        expense_type = request.form.get('expense')
        coltwo=-1
        if(expense_type!='EQUAL' and expense_type!='EXACT'):
            col2 = request.form.getlist('coltwo')
            if expense_type=="ADJUST":
                coltwo = [x for x in col2 if float(x)>=0]
            else:
                coltwo = [x for x in col2 if float(x)>0]
            print(coltwo)
        print(coltwo)
        con_amt = [x for x in consumer_amount if float(x)>0]
        entry_item(pool_id, description, date, amount, payer_name[0], consumer, con_amt,expense_type,coltwo)
        print(request.form)
        
       
        return redirect(url_for('pool_items', pool_link=pool_link))

    return render_template('create_item.html', pool_link=pool_link, participant_names = participants)

@app.route('/<pool_link>/items/edit/<int:item_id>', methods=('GET', 'POST'))
def edit_item(pool_link, item_id):
 
    pool_id = get_pool_id(pool_link)
    participants =list(get_participants_name(pool_id))
    if item_exists(item_id) != -1:
        item, consumers = get_item(item_id)
        consumers_names = [x[0] for x in consumers]
        consumers_ids = [x[2] for x in consumers]
    notpaidby = []
    for participant in participants:
        if(participant[0]!=item[3]):
            notpaidby.append(participant[0])
    
    notconsumer = []
    consumer = []
    for participant in participants:
        if(participant[0] in consumers_names):
            consumer.append(participant[0])
        else:
            notconsumer.append(participant[0])
     
    print(item)
   
    col2_values = []
    expense_type=item[4]
    print(expense_type)
    if(expense_type!='EQUAL' and expense_type!='EXACT'):
        col2_values=get_coltwo(consumers_ids)
        
    if request.method == "POST":
        
        action = request.form.get('submit-btn')
        description = request.form.get('description')
        date = request.form.get('date')
        amount = request.form.get('amount')
        payer_name = request.form.get('payerName')
        consumer = request.form.getlist('consumer_name')
        consumer_amount = request.form.getlist('consumer_amount')
        expense_type = request.form.get('expense')
        coltwo=-1
        if(expense_type!='EQUAL' and expense_type!='EXACT'):
            col2 = request.form.getlist('coltwo')
            if expense_type=="ADJUST":
                coltwo = [x for x in col2 if float(x)>=0]
            else:
                coltwo = [x for x in col2 if float(x)>0]
            print(coltwo)
        print(coltwo)
        con_amt = [x for x in consumer_amount if float(x)>0]   
        update_item(pool_id,item_id, description, date, amount, payer_name, consumer, con_amt, expense_type,coltwo,item,consumers)
        return redirect(url_for("pool_items", pool_link=pool_link))

    return render_template('edit_item.html',item=item,consumers=consumers,excludedp=notpaidby,notconsumer=notconsumer,consumer=consumer,expense_type=expense_type,col2_values=col2_values,participant_names=participants, pool_link=pool_link)


# display single item
@app.route('/<pool_link>/items/view/<int:item_id>/')
def display_item(pool_link, item_id):
    if item_exists(item_id) != -1:
        item, consumers = get_item(item_id)
        print(item, consumers[0])
        return render_template('ditem.html', item=item, consumers=consumers, pool_link=pool_link)
    else:
        abort(404)


# about page
@app.route('/about/')
def about_page():
    return render_template('about.html')


if __name__ == '__main__':
    app.run()
