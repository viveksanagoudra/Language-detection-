from flask import Flask, flash,redirect,render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import Engine, engine_from_config
from flask_login import login_required, logout_user,LoginManager,login_user,login_manager,current_user
from sqlalchemy import create_engine
from sqlalchemy import Join



#! my database connection
local_server=True
app=Flask(__name__)
app.secret_key="SecretKey"



#! this is for getting unique user access
login_manager=LoginManager(app)
login_manager.login_view='login'



app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/delivery'
db=SQLAlchemy(app)


@login_manager.user_loader
def load_user(user_id):
    return users.query.get(int(user_id))


#!----------------------------------------------------------Class for all tables used------------------------------------------------------------------------------------
class assignment(db.Model, UserMixin):
    OrderID=db.Column(db.Integer,primary_key=True)
    AgentID=db.Column(db.Integer)
    CustomerID=db.Column(db.Integer)
    def get_id(self):
        return int(self.OrderID)
    
class users(db.Model, UserMixin):
    Id=db.Column(db.Integer,primary_key=True)
    Password=db.Column(db.String(1000))
    Position=db.Column(db.String(1000))
    def get_id(self):
        return int(self.Id)
    
class status(db.Model, UserMixin):
    OrderID=db.Column(db.Integer,primary_key=True)
    AgentID=db.Column(db.Integer)
    status=db.Column(db.String(1000))
    def get_id(self):
        return int(self.OrderID)
    
class orders(db.Model, UserMixin):
    OrderID=db.Column(db.Integer,primary_key=True)
    CustomerID=db.Column(db.Integer)
    OrderDate=db.Column(db.String(1000))
    DeliveryDate=db.Column(db.String(1000))
    def get_id(self):
        return int(self.OrderID)
    
class customer(db.Model, UserMixin):
    Id=db.Column(db.Integer,primary_key=True)
    Name=db.Column(db.String(1000))
    Location=db.Column(db.String(1000))
    Contact=db.Column(db.BigInteger)
    def get_id(self):
        return int(self.OrderID)
    

#!-------------------------------------------------------------------End of class------------------------------------------------------------------------------------------




#!---------------------------------------------------------------Routing for all pages-------------------------------------------------------------------------------------
@app.route("/")
def home():
    return render_template("base.html")

@app.route("/About")
def Index():
    return render_template("About.html")

@app.route("/AdminLogin")
def AdminLogin():
    return render_template("AdminLogin.html")

@app.route("/DManagerLogin")
def DMLogin():
    return render_template("DManagerLogin.html")

@app.route("/LManagerLogin")
def LMLogin():
    return render_template("LManagerLogin.html")

@app.route("/AgentLogin")
def ALogin():
    return render_template("AgentLogin.html")

@app.route("/Add")
def Add():
    return render_template("Add.html")

@app.route("/Delete")
def delete():
    return render_template("Delete.html")

@app.route("/Admin")
def Admin():
    return render_template("Admin.html")

@app.route("/LManager")
def LManager():
    return render_template("LManager.html")

@app.route("/Check", methods=["GET", "POST"])
def index():
    return render_template("Assignment.html")

@app.route("/Agent")
def Agent():
    return render_template("Agent.html")

@app.route("/Update")
def Update():
    return render_template("Update.html")

@app.route("/Assign")
def Assign():
    return render_template("Assign.html")

@app.route("/Orders")
def Orders():
    return render_template("ADDorders.html")

@app.route("/DManager")
def DManager():
    return render_template("DManager.html")

@app.route("/DeleteO")
def DeleteO():
    return render_template("DeleteOrders.html")

@app.route("/AddCust")
def AddCust():
    return render_template("AddCust.html")

#!--------------------------------------------------------------------End of routing------------------------------------------------------------------------------






#!--------------------------------------------------------------------Logging out------------------------------------------------------------------------------
@app.route("/Logout")
def logout():
    session.pop('user_id', None)
    flash('You have been logged out successfully!', 'success')
    return redirect("/")
#!--------------------------------------------------------------------End of logging out------------------------------------------------------------------------------






#!--------------------------------------------------------------------------login part----------------------------------------------------------------------------
@app.route('/AdminLogin', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        Id = request.form.get('Id')
        Password = request.form.get('Password')
        user = users.query.filter_by(Id=Id).first()
        if user and user.Password==Password and user.Position=='Admin' :
            login_user(user)
            flash("Logged in successfully","success")
            return render_template('Admin.html')
        else:
            flash("⚠️ Login failed, check credentials","warning")
            return render_template('AdminLogin.html')

@app.route('/AgentLogin', methods=['POST', 'GET'])
def login1():
    if request.method == "POST":
        Id = request.form.get('Id')
        Password = request.form.get('Password')
        user = users.query.filter_by(Id=Id).first()
        if user and user.Password==Password and user.Position=='Agent' :
            login_user(user)
            flash("Logged in successfully","success")
            return render_template('Agent.html')
        else:
            flash("⚠️ Login failed, check credentials","warning")
            return render_template("AgentLogin.html")

@app.route('/DManagerLogin', methods=['POST', 'GET'])
def login2():
    if request.method == "POST":
        Id = request.form.get('Id')
        Password = request.form.get('Password')
        user = users.query.filter_by(Id=Id).first()
        if user and user.Password==Password and user.Position=='DManager' :
            login_user(user)
            flash("Logged in successfully","success")
            return render_template('DManager.html')
        else:
            flash("⚠️ Login failed, check credentials","warning")
            return render_template("DManagerLogin.html")


@app.route('/LManagerLogin', methods=['POST', 'GET'])
def login3():
    if request.method == "POST":
        Id = request.form.get('Id')
        Password = request.form.get('Password')
        user = users.query.filter_by(Id=Id).first()
        if user and user.Password==Password and user.Position=='LManager' :
            login_user(user)
            flash("Logged in successfully","success")
            return render_template('LManager.html')
        else:
            flash("⚠️ Login failed, check credentials","warning")
            return render_template("LManagerLogin.html")
#!------------------------------------------------End of login part (for all 4 users)---------------------------------------------------------------------      





# !----------------------------------------------------------Querying------------------------------------------------------------------------------------- 
#Adding user into table users
@app.route('/Add',methods=['POST','GET'])
def add():
    if request.method=="POST":
        Id=request.form.get('Id')
        Password=request.form.get('Password')
        Position=request.form.get('Position')
        user=users.query.filter_by(Id=Id).first()
        if user :
            flash("⚠️ User already exists ","warning")
            return render_template("Add.html")
        #passing the values into the table "users" in delivery database
        new_user=users(Id=Id,Password=Password,Position=Position)
        db.session.add(new_user)
        db.session.commit()      
        flash("New user added successfully","success")
        return render_template("Add.html")
    return render_template("Add.html")


#Deleting a user from table users
@app.route('/Delete', methods=['POST','GET'])
def delete_item():
    if request.method=="POST":
        id=request.form.get('Id')
        item = users.query.get(id)
        if item and item.Position !='Admin' :
            db.session.delete(item)
            db.session.commit()
            flash('User deleted successfully!', 'success') 
            return render_template("Delete.html")
        elif item and item.Position=='Admin' :
            flash('⚠️ Cannot delete user', 'warning')  
            return render_template("Delete.html")
        else:
            flash('⚠️ User does not exist', 'warning')  
            return render_template("Delete.html")
    return render_template("Delete.html")


#Retrieving data about the deliveries assigned to the agent
@app.route('/Retrieve', methods=['POST', 'GET'])
def fetch_data_by_id():
    if request.method == "POST":
        Id = request.form.get('Id')
        try:
            assignments = db.session.query(assignment, customer).select_from(assignment).join(customer, assignment.CustomerID == customer.Id).filter(assignment.AgentID == Id).all()
            print(assignments)
            return render_template("AssignmentDisplay.html", assignments=assignments)
        except Exception as e:
            print(e)
            flash('⚠️ Error fetching data', 'warning')
            return render_template("Assignment.html", error="Error fetching data")
    return render_template("Assignment.html")


#Retrieving delivery status
@app.route('/Dstatus')
def Dstatus():
    try :    
            dstatus = status.query.all()
            return render_template("statusdisplay.html", dstatus=dstatus)
    except Exception as e:
            flash('⚠️ Error fetching data', 'warning')
            return render_template("statusdisplay.html", error="Error fetching data")


#updating delivery status
@app.route('/Update',methods=['POST','GET'])
def Update_status():
    if request.method=="POST":
        Id=request.form.get('Id')
        new_status=request.form.get('status')
        print(Id,new_status)
        Dstatus=status.query.filter_by(OrderID=Id).first()
        if not Dstatus :
            flash("⚠️ No assigned deliveries found for entered OrderID","warning")
            return render_template("Update.html")
        Dstatus.status=new_status
        try:
            db.session.commit()
            flash("✅ Status updated successfully", "success")
        except Exception as e:
            flash(f"❌ Error updating status: {e}", "danger")
        return render_template("Update.html")
    return render_template("Update.html")


#Assigning deliveries to agents
@app.route('/Assign',methods=['POST','GET'])
def assign():
    if request.method=="POST":
        OrderId=request.form.get('OID')
        AgentId=request.form.get('AID')
        CustomerId=request.form.get('CID')
        user=assignment.query.filter_by(OrderID=OrderId).first()
        user1=orders.query.filter_by(OrderID=OrderId).first()
        if user :
            flash("⚠️ Delivery already assigned ","warning")
            return render_template("Assign.html")
        #Assigning deliveries to agents and at the same time updating the delivery status in the status table for the newly assigned order
        if user1 :
            new_user=assignment(OrderID=OrderId,AgentID=AgentId,CustomerID=CustomerId)
            new_user1=status(OrderID=OrderId,AgentID=AgentId,status="undelivered")
            db.session.add(new_user)
            db.session.commit()      
            db.session.add(new_user1)
            db.session.commit()
            flash("Delivery assigned successfully","success")
            return render_template("Assign.html")
        else :
            flash("⚠️ OrderID does not correspond to any active orders ","warning")
            return render_template("Assign.html")
    return render_template("Assign.html")


#Retreiving information about all active orders
@app.route('/GetOrInfo')
def GetOrInfo():
    try :    
            data = orders.query.all()
            return render_template("order.html", data=data)
    except Exception as e:
            flash('⚠️ Error fetching data', 'warning')
            return render_template("order.html", error="Error fetching data")


#Adding order data into table orders
@app.route('/Orders',methods=['POST','GET'])
def AddOrders():
    if request.method=="POST":
        OrderId=request.form.get('OID')
        CustomerId=request.form.get('CID')
        OrderDate=request.form.get('OD')
        DelDate=request.form.get('EDD')
        Loc=request.form.get('LOC')
        user=orders.query.filter_by(OrderID=OrderId).first()
        user1=customer.query.filter_by(Id=CustomerId).first()
        if user :
            flash("⚠️ Order already exists ","warning")
            return render_template("ADDorders.html")
        if user1 :
            new_user=orders(OrderID=OrderId,CustomerID=CustomerId,OrderDate=OrderDate,DeliveryDate=DelDate)
            db.session.add(new_user)
            db.session.commit()      
            flash("Order details added successfully","success")
            return render_template("ADDorders.html")
        else :
            flash("⚠️ No such customer exists, check customer ID ","warning")
            return render_template("ADDorders.html")
    return render_template("ADDorders.html")


#Deleting a user from table users
@app.route('/DeleteO', methods=['POST','GET'])
def deleteO():
    if request.method=="POST":
        id=request.form.get('Id')
        item = orders.query.get(id)
        item1 = status.query.get(id)
        if item and item1 and item1.status !='undelivered' :
            db.session.delete(item)
            db.session.commit()
            flash('Order deleted successfully!', 'success') 
            return render_template("DeleteOrders.html")
        elif item and item1 and item1.status=='undelivered' :
            flash('⚠️ order has been assigned for delivery and is in transit', 'warning')  
            return render_template("DeleteOrders.html")
        elif item  :
            db.session.delete(item)
            db.session.commit()
            flash('Order deleted successfully!', 'success') 
            return render_template("DeleteOrders.html")
        else:
            flash('⚠️ order does not exist', 'warning')  
            return render_template("DeleteOrders.html")
    return render_template("DeleteOrder.html")

#Adding customer details into table customer
@app.route('/AddCust',methods=['POST','GET'])
def addcust():
    if request.method=="POST":
        Id=request.form.get('Id')
        Name=request.form.get('Name')
        Location=request.form.get('Location')
        Contact=request.form.get('Contact')
        cust=customer.query.filter_by(Id=Id).first()
        if cust :
            flash("⚠️ customer already exists ","warning")
            return render_template("AddCust.html")
        #passing the values into the table "users" in delivery database
        new_user=customer(Id=Id,Name=Name,Location=Location,Contact=Contact)
        db.session.add(new_user)
        db.session.commit()      
        flash("New customer added successfully","success")
        return render_template("AddCust.html")
    return render_template("AddCust.html")
#!----------------------------------------------------------End of Querying------------------------------------------------------------------------------------- 


#testing whether db is connected or not
@app.route("/test")
def test():
    try:
        a=users.query.all()
        print(a)
        return f'My database has been connected'
    except Exception as e:
        print(e)
        return f'My database is not connected {e}'
app.run(debug=True)


