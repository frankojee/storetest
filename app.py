from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask.globals import request
from flask.signals import message_flashed
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, form, validators, IntegerField, DateTimeField
from passlib.hash import sha256_crypt
from functools import wraps
import datetime
# from flask.templating import render_template


app = Flask(__name__)

#config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'ojee'
app.config['MYSQL_PASSWORD'] = '12345'
app.config['MYSQL_DB'] = 'store_app'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

#checking if logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if 'logged_in' in session:
            return f(*args,**kwargs)
        else:
            flash('Unauthorized,kindly login','danger')
            return redirect(url_for('home'))
    return wrap

#logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('logged out','success')
    return redirect(url_for('admin_login'))
#customer logout
@app.route('/customerlogout')
@is_logged_in
def costomerlogout():
    session.clear()
    flash('logged out','success')
    return redirect(url_for('customer_login'))
        





@app.route('/products')
def products():
    pass


@app.route('/guide')
def guide():
    pass
   
        

#employees register form class
class employee_register_class(Form):
    first_name = StringField('First Name',[validators.Length(min=1,max=30)])
    sir_name = StringField('Sir Name',[validators.Length(min=1,max=20)])
    role = StringField('Role',[validators.length(min=1,max=20)])
    email = StringField('Email',[validators.length(min=1,max=30)])
    tel = StringField('Tel',[validators.length(min=1,max=30)])

#employee registration
@app.route('/employee_register', methods=['POST','GET'])
def employee_register():
    #making the form by a request and creating its instance
    form = employee_register_class(request.form)
    if request.method == 'POST' and form.validate():
        first_name = form.first_name.data
        sir_name = form.sir_name.data
        role = form.role.data
        email = form.email.data
        tel = form.tel.data

        #creating the cursor
        cur = mysql.connection.cursor()
        #executing
        cur.execute("INSERT INTO employees(first_name, sir_name, role, email,tel) VALUES('{}','{}','{}','{}','{}')".format(first_name, sir_name, role, email, tel))
        mysql.connection.commit()
        cur.close()
        flash("New employee added",'success')

    return render_template('employee_register.html',form=form)


                



#customer register form class
class customers_register_class(Form):
    name = StringField('Name',[validators.Length(min=1,max=50)])
    user_name = StringField('User Name',[validators.Length(min=1,max=30)])
    email = StringField('Email',[validators.Length(min=1, max=30)])
    tel = StringField('Tel',[validators.Length(min=1, max=20)])
    address = StringField('Address',[validators.Length(min=1, max=30)])
    postal_code = StringField('Postal Code',[validators.Length(min=1, max=30)])
    city = StringField('City',[validators.Length(min=1, max=30)])
    county = StringField('County',[validators.Length(min=1, max=30)])
    password = PasswordField('Password',[
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Password do not match')
    ])
    confirm = PasswordField('Confirm Password')
    basis = StringField('Basis',[validators.Length(min=1, max=30)])
    credit_card = StringField('Credit Card No.',[validators.Length(min=0, max=30)])
    debit_card = StringField('Debit Card No.',[validators.Length(min=0, max=30)])
#customer registration
@app.route('/customer_register', methods = ['GET','POST'])
def customer_registration():
    form = customers_register_class(request.form)

    if request.method == 'POST' and form.validate():
        name = form.name.data
        user_name = form.user_name.data
        email = form.email.data
        tel = form.tel.data
        address = form.address.data
        postal_code = form.postal_code.data
        city = form.city.data
        county = form.county.data
        password = sha256_crypt.encrypt(str(form.password.data))
        basis = form.basis.data
        credit_card = form.credit_card.data
        debit_card = form.debit_card.data
        

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO customers(name, user_name, e_mail ,tel, address, postal_code, city, county, password, basis, debit_card,credit_card_info) VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(name,user_name,email,tel,address,postal_code,city,county,str(password),basis,debit_card,credit_card))
        mysql.connection.commit()
        cur.close()
        flash('Successful registration','success')
        return redirect(url_for('customer_login'))
    return render_template('customer_register.html',form=form)

@app.route('/customer_login', methods={'GET','POST'})
def customer_login():
    if request.method == 'POST':
        user_name = request.form['username']
        password_candidate = request.form['password']
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM customers WHERE user_name = '{}' ".format(user_name))
        if result > 0:
         info = cur.fetchone()
         password = info['password']
         #password verification
         if sha256_crypt.verify(password_candidate,password):
             app.logger.info('Matching password')

             #passed
             session['logged_in'] = True
             session['user_name'] = user_name

             flash('You are logged in','success')
             cur.close()
             return redirect(url_for('ProductDisplay'))
         else:
                error = 'Invalid login'
                app.logger.info('Non matching passswords')
                cur.close()
                return render_template('customer_login.html', error=error)
        else:
            error = "Unknown user"
            return render_template('customer_login.html', error=error)
    return render_template('customer_login.html')


#stores form
class store_register(Form):
    store_name = StringField('Store Name',[validators.Length(min=1,max=30)])
    county = StringField('County',[validators.Length(min=1,max=30)])
    town = StringField('Town',[validators.length(min=1,max=30)])

@app.route('/store_register.html', methods = ['GET','POST'])
def store_registration():
    form = store_register(request.form)
    if request.method == 'POST' and form.validate():
        store_name = form.store_name.data
        county = form.county.data
        town = form.town.data

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO stores(store_name,county,town) VALUES({},{},{}".format(store_name,county,town))
        cur.commit()
        cur.close()
    return render_template('store_register.html',form = form)


#admin form
class admin_assign(Form):
    userid = StringField('Employment',[validators.Length(min=0,max=30)])
    role = StringField('Role',[validators.Length(min=1,max=30)])
    password = PasswordField('Password',[
        validators.DataRequired(),
        validators.EqualTo('confirm',message='Non-matching passwords')
    ])
    confirm = PasswordField('Confirm Password')

@app.route('/admin_add', methods = ['GET','POST'])
def admin_add():
    form = admin_assign(request.form)
    if request.method == 'POST' and form.validate():
        employment_id = form.employment_id.data
        role = form.role.data
        password = sha256_crypt.encrypt(str(form.password.data))
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(employment_id,role,password) VALUES('{}','{}','{}')".format(employment_id,role,password))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('admin_login'))
    return render_template('admin_add.html',form=form)

#since the data is in the DB, form class isn't required
#the form class handlesthe data b4 they are passed to the DB
#admin login
@app.route('/admin_login', methods = ['GET','POST'])
def admin_login():
    if request.method =='POST':
        #Getting form fields
        role = request.form['role']
        password_candidate = request.form ['password']
        cur = mysql.connection.cursor()

        #getting admin by employment id
        result = cur.execute("SELECT * FROM users WHERE role = %s",[role])

        #verifying the password
        if result > 0:
            #getting the store passwords(hash)
            Data = cur.fetchone()
            password = Data['password']

            #passwords comparison
            if sha256_crypt.verify(password_candidate,password):
                app.logger.info('Matching password')

                #passed
                session['logged_in'] = True
                session['role'] = role

                flash('You are logged in','success')
                cur.close()
                if role == 'customer_service':
                    pass
                elif role == 'call_centre':
                    pass
                elif role == 'stocking_clerk':
                    pass
                elif role == 'marketing':
                    pass
                return redirect(url_for('admin_dashboard'))
            else:
                error = 'Invalid login'
                app.logger.info('Non matching passswords')
                cur.close()
                return render_template('admin_login.html', error=error)
        else:
            error = 'role not found'
            return render_template('admin_login.html', error=error)
    return render_template('admin_login.html')


#Products
class ProductForm(Form):
    type_id = IntegerField('Type Id')
    product_name = StringField('Product Name',[validators.Length(min=1,max=30)])
    price = IntegerField('Price')
    summary = TextAreaField('Summary',[validators.Length(min=1)])
    src = TextAreaField('Image Source',[validators.Length(min=1)])

#adding products
@app.route('/add_products', methods=['POST','GET'])
def add_products():
   form = ProductForm(request.form)
   if request.method == 'POST' and form.validate():
       typeId=form.type_id.data
       name=form.product_name.data
       price=form.price.data
       summary=form.summary.data
       src=form.src.data

       cur = mysql.connection.cursor()
       cur.execute("INSERT INTO products(type_id, product_name, price, summary, src) VALUES('{}', '{}', '{}', '{}', '{}')".format(typeId, name, price, summary, src))
       mysql.connection.commit()
       cur.close()
       flash("Product added", 'success')
       return redirect(url_for('admin_dashboard'))
   return render_template('add_products.html', form = form)
#admin product view
@app.route('/adminproductview', methods = ['GET', 'POST'])
@is_logged_in
def adminproductview():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM products")
    items = cur.fetchall()
    if result > 0:
        cur.close()
        return render_template('adminproductview.html', items = items)
    else:
        msg="No product found"
        cur.close()
        return render_template('adminproductview.html', msg = msg)

#editing products 
@app.route('/edit_product/<string:id>', methods = ['GET','POST'])
def edit_product(id):
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM products WHERE id ={}".format(id))
    product = cur.fetchone()
    form = ProductForm(request.form)
    #populating the form fields with their values
    form.type_id.data = product['type_id']
    form.product_name.data = product['product_name']
    form.price.data = product['price']
    form.summary.data = product['summary']
    form.src.data = product['src']
    if request.method == 'POST' and form.validate():
        type_id = request.form['type_id']
        product_name = request.form['product_name']
        src = request.form['src']
        price = request.form['price']
        summary = request.form['summary']

        cur = mysql.connection.cursor()
        cur.execute("UPDATE products SET type_id ='{}',src = '{}', product_name = '{}', price = '{}', summary = '{}' WHERE id = '{}'".format(type_id,src,product_name,price,summary,id))
        mysql.connection.commit()
        cur.close()
        flash('Product Updated','success')
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_product.html',form=form)

#products display
@app.route('/ProductDispaly')
#@is_logged_in
def ProductDisplay():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM products")
    items = cur.fetchall()
    if result > 0:
        cur.close()
        return render_template('ProductDisplay.html', items=items)
    else:
        msg="No product found"
        cur.close()
        return render_template('ProductDisplay.html', msg = msg)

@app.route('/')
#def index():
    #return render_template('home.html')
def ProductDisplay_2():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM products")
    items = cur.fetchall()
    if result > 0:
        cur.close()
        return render_template('ProductDisplay_2.html', items=items)
    else:
        msg="No product found"
        cur.close()
        return render_template('ProductDisplay_2.html', msg = msg)



 #Deleting products
@app.route('/delete_product/<string:id>', methods=['POST'])   
@is_logged_in
def delete_product(id):
    cur=mysql.connection.cursor()
    cur.execute("DELETE FROM products WHERE id = '{}' ".format(id))
    mysql.connection.commit()
    cur.close()
    
    
    flash('Product Deleted','success')
    return redirect(url_for('admin_dashboard'))


#admin's dashboard
@app.route('/admin_dashboard')
@is_logged_in
def admin_dashboard():
   return render_template('admin_dashboard.html')
    
#suppliers
#suppliers form
class supplierdetails(Form):
    company_name = StringField('Co. Name', [validators.length(min=1,max=50)])
    address = StringField('Address',[validators.Length(min=1, max=30)])
    postal_code = StringField('Postal Code',[validators.Length(min=1, max=30)])
    city = StringField('City',[validators.Length(min=1, max=30)])
    email = StringField('Email',[validators.Length(min=1, max=30)])
    tel = StringField('Tel',[validators.Length(min=1, max=20)])

@app.route('/supplieradd', methods = ['GET','POST'])
def supplieradd():
    form = supplierdetails(request.form)
    if request.method == 'POST' and form.validate():
        company_name = form.company_name.data
        address = form.address.data
        postal_code = form.postal_code.data
        city = form.city.data
        email = form.email.data
        tel = form.tel.data

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO companies(company_name, address,postalcode,city,email,tel) VALUES('{}','{}','{}','{}','{}','{}')".format(company_name, address,postal_code,city,email,tel))
        mysql.connection.commit()
        cur.close()
        flash('supplier added','success')
        return redirect(url_for('admin_dashboard'))
    return render_template('supplieradd.html',form=form)



#Type
#Type form
class product_type(Form):
    name = StringField('Type', [validators.length(min=1,max=50)])
    companyId = StringField('Supplier ID', [validators.length(min=1,max=50)])
@app.route('/addproducttype', methods=['POST','GET'])
def addproducttype():
    form = product_type(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        companyid = form.companyId.data
        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO product_type(name,company_id) VALUES('{}','{}')".format(name,companyid))
        mysql.connection.commit()
        cur.close()
        flash('New product type added','success')
        return redirect(url_for('admin_dashboard'))
    return render_template('typeadd.html', form=form)

#sales
#sales class
class sales():
    item = StringField('Item',[validators.Length(min=1,max=30)])
    dateordered = DateTimeField('Date Ordered')
    quantity = IntegerField('Quantity')
    delivery = DateTimeField('Delivery Date')
    shipping = StringField('Shipping Co.',[validators.Length(min=1,max=30)])

@app.route('/buy/<string:id>', methods = ['GET','POST'])
def buy(id):
    cur = mysql.connection.cursor()
    item = cur.fetchone()
    form = sales(request.form)
    form.item.data = item['item']
    form.dateordered.data = datetime.datetime.today()
    form.delivery.data = Previous_Date = datetime.datetime.today() + datetime.timedelta(days=14)




if __name__ =='__main__':
    app.secret_key = 'ojee'
    app.run(debug=True)
