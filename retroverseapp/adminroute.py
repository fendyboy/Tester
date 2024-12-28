import os,secrets
from flask import Flask,render_template,redirect,request,flash,session,url_for
from flask_mail import Message
from werkzeug.security import generate_password_hash,check_password_hash
from retroverseapp import app,mail
from retroverseapp.model import Admin,db,Product,Customer,Order
from retroverseapp.form import ProductForm



@app.errorhandler(404)
def mypagenotfound(error):    	
    return render_template('admin/error.html',error=error), 404


@app.route('/admindash/',methods=['GET','POST'])
def admindashboard():
    Adminid = session.get('Adminid')
    print("Session Admin ID:", Adminid)  # Debugging line
    if  Adminid:

        if request.method == 'GET':
            return render_template('admin/dashboard.html')
        else:
            productid=request.form.get('productsid')
            productname=request.form.get('productsname')
        
            if productid == '' or productname == '':
                flash('The fields are empty')
                return redirect('/adminlogin/')
            
            findprod=db.session.query(Product).filter(Product.id==productid, Product.name==productname).first()
            if findprod:
                db.session.delete(findprod)
                db.session.commit()
                flash('Product deleted sucessfully')
            else:
                flash('There is no product with that product id')
            return redirect('/admindash/')
    else:
        flash('You are not login')            
        return  redirect('/adminlogin/')



@app.route('/adminsignup/',methods=['GET','POST'])
def signin():
    if  request.method == 'GET':
        return render_template('admin/signup.html')
    else:
        username = request.form.get('username')
        password =  request.form.get('password')
        email = request.form.get('email')
        confirmpassword =  request.form.get('confirmpassword')
        if  username == '' or  password == '' or email == '' :
            flash('All fields must  be filled')
            return render_template('admin/signup.html')
        elif  password != confirmpassword:
            flash('The password dont match')
            return render_template('admin/signup.html')
        else:
            hashpassword = generate_password_hash(password)
            admin = Admin(username=username,email=email,password_hash=hashpassword)
            try:
                db.session.add(admin)
                db.session.commit()
                admin_id=admin.id
                session['Adminid']=admin_id
                flash('Account created successfully')
                return render_template('admin/dashboard.html')
            except:
                flash('Account already exists')
                return render_template('admin/signup.html')
            

@app.route('/adminlogin/', methods=["GET","POST"])
def adminlogin():
    if request.method == 'GET':
        return render_template('admin/login.html')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        verify = db.session.query(Admin).filter(Admin.username==username).first()
        print("Admin Found:", verify)
        if verify:
            passhash=verify.password_hash
            check=check_password_hash(passhash,password)
            if check == True:
                session['Adminid']=verify.id
                print("Admin ID set in session:", session['Adminid'])
                return render_template('admin/dashboard.html')
            else:
                flash('Incorrect password')
                return redirect('/adminlogin/')
        else:
            flash('Username does not exist')
        return render_template('admin/login.html')

# @app.route('/products/', methods=['GET', 'POST'])
# def products():
#     form = ProductForm()
#     products_id = session.get('products_id')
#     if request.method == 'GET':
#         return render_template('admin/products.html',form=form)
#     else:
#         if form.validate_on_submit():
#         # Handling form data
#             productname = form.productname.data
#             productdescription = form.productdescription.data
#             productprice = form.productprice.data
#             productimage = form.productimage.data
#             sizes = form.sizes.data
#             category = form.category.data
            
#             original_filename=productimage.filename
            
#             products = db.session.query(Product).get(products_id)

#             if products_id is None:
#                 # Create a new product
#                 products = Product()
            

#             if  original_filename != '' :
#                 ext = os.path.splitext(original_filename)
#                 extension = ext[-1]
#                 newname=secrets.token_hex(11)
#                 productimage.save("retroverseapp/static/images" +  newname + extension)

#                 products.image = newname + extension
            
#             products.name=productname
#             products.description=productdescription
#             products.price=productprice
#             products.size=sizes
#             products.category_id=category
#             db.session.add(products)
#             db.session.commit()
#             flash('Product added successfully')
#             return redirect('/products/')
#         else:
#             return render_template('admin/products.html',form=form)
    
@app.route('/products/', methods=['GET','POST'])
def products():
    Admin_id = session.get('Adminid')
    prodform = ProductForm()
    if Admin_id: #user is logged in

        if request.method == 'GET':
            
            return render_template('admin/products.html',prodform=prodform)
        else: ## means they are submitting form by post
            if prodform.validate_on_submit(): ## validate form data, retrive data and update details in db
                prodname = prodform.productname.data
                proddescription = prodform.productdescription.data
                prodprice = prodform.productprice.data
                prodimage = request.files.get('productimage')
                prodsize = prodform.sizes.data
                prodcat = prodform.category.data
                prodTag = prodform.Tag.data
                ## getting the filename and getting the extension
                original_filename = prodimage.filename
                
                new_product = Product()
                ## users can update other details wthout uploading a new file
                if original_filename != '':
                    ext = os.path.splitext(original_filename) ## splitting the file on the extension
                    extension = ext[-1]

                    ## generate new name
                    newfilename = secrets.token_hex(10)
                    prodimage.save("retroverseapp/static/images/"+newfilename+extension)

                    new_product.image =  newfilename+extension

                    print("Image file path:", new_product.image)  # Print out the image file path
                    if not os.path.exists("retroverseapp/static/images/"+newfilename+extension):  # Check if the image file exists
                        print("Image file does not exist")
                    else:
                        print("Image file exists")

                ## creating an object and putting it into the database
                
                new_product.name = prodname
                new_product.description = proddescription
                new_product.price = prodprice
                new_product.size = prodsize
                new_product.category_id = prodcat
                new_product.tags=prodTag
                db.session.add(new_product)
                db.session.commit()

                

                ## upload file using flask form
                flash('File successful updated')
                return redirect (url_for('products'))
            else:
                
                return render_template('admin/products.html',prodform=prodform)


    else: #this means session is None
        flash('You need to login to access to this page','error')
        return redirect('/adminlogin/')
# @app.route('/admincontact/',methods=['GET','POST'])
# def admincontact():
    
#     if request.method == 'GET':
#         return render_template('admin/contact.html')
#     else:
#         id=request.form.get('customerid')
#         user=db.session.query(Customer).filter_by(id=id).first()
#         message=request.form.get('message')
#         msg=Message(subject='Contact Email',sender='oponeboboola@gmail.com',recipients=[user.email])
#         msg.html = f'''<p style="background-color:blue;color:white;padding:30px;">{message}</p>'''
#         #msg.body= message
        
        
#         mail.send(msg)
#         flash('Message sent successfully')
#         return redirect(url_for('admincontact'))
# @app.route('/deleteproduct/', methods=["GET","POST"])
# def deleteproduct():
    

@app.route('/customerspage/',methods=['GET','POST'])
def  customerspage():
    customer_count = db.session.query(Customer).count()
    cust = db.session.execute(db.text('SELECT firstname,lastname,username,email,address,phone FROM customer'))
    customers=cust.fetchall()
    if request.method == 'GET':
        return render_template('admin/customers.html',customers=customers,customer_count=customer_count)
    else:
        id=request.form.get('customerid')
        user=db.session.query(Customer).filter_by(id=id).first()
        message=request.form.get('message')
        msg=Message(subject='Contact Email',sender='oponeboboola@gmail.com',recipients=[user.email])
        msg.html = f'''
    <div style="background-color:#ffffff; color:#000000; font-family:Arial, sans-serif; padding:20px;">
        <!-- Header with Logo -->
        <div style="text-align:center; padding:20px; background-color:#000000;">
            <h1 style="color:#ffffff; margin:0; text-transform:uppercase;">Retroverse</h1>
        </div>
        
        <!-- Hero Section with Message -->
        <div style="padding:40px; text-align:center; background-color:#f5f5f5;">
            <h2 style="font-size:28px; font-weight:bold; color:#000;">Your Style, Redefined</h2>
            <p style="color:#333; font-size:16px; line-height:1.6;">
                Welcome to Retroverse! Explore our latest collection and elevate your fashion game.
            </p>
            {message}
        </div>

        <!-- Call to Action -->
        <div style="text-align:center; padding:20px; background-color:#000000;">
            <a href="#" style="font-size:18px; font-weight:bold; color:#ffffff; text-decoration:none; background-color:#000000; padding:12px 24px; border:2px solid #ffffff;">
                Shop Now
            </a>
        </div>

        <!-- Footer with Social Links -->
        <div style="padding:20px; text-align:center; background-color:#f5f5f5; color:#333;">
            <p>Thank you for being part of Retroverse!</p>
            
            <p>&copy; 2024 Retroverse. All rights reserved.</p>
        </div>
    </div>
'''

        #msg.body= message
        
        
        mail.send(msg)
        flash('Message sent successfully')
        return redirect(url_for('customerspage'))


@app.route('/report/',methods=['POST','GET'])
def report():
    if request.method == 'GET':
        return render_template('user/contact.html')
    else:
        name=request.form.get('name')
        email=request.form.get('email')
        message=request.form.get('message')
        if email == ''  or name == '' or message == '':
            flash('Please fill all the fields')
        else:

            msg = Message(subject='Retroverse Report Email', sender=email, recipients=['oponeboboola@gmail.com'])
        

            msg.body = f"Name: {name}\nEmail: {email}\nMessage: {message}"
        
        
            mail.send(msg)
            flash('Message sent successfully')
            return redirect(url_for('conatct'))
        return render_template('user/contact.html')
@app.route('/customersorders/',methods=['GET','POST'])
def  customersorders():
    customer_order = db.session.query(Order).count()
    cust = db.session.execute(db.text('SELECT order_date,status,total_amount FROM Order'))
    order=cust.fetchall()
    return render_template('admin/order.html',orders=customer_order)
