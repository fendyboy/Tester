import requests
import random
import json

from flask import flash,Flask,render_template,request,session,redirect,url_for,jsonify
from werkzeug.security import generate_password_hash,check_password_hash
from decimal import Decimal

from retroverseapp import app
from retroverseapp.model import State,db,Customer,Product,Order,OrderItem,Wishlist
import traceback




@app.route('/signup/',methods=['GET','POST'])
def signup():
    if request.method == 'GET':
        states = db.session.query(State).all()
        return render_template('user/signup.html',states=states)
    else:
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        confirmpassword = request.form.get('confirmpassword')
        phone=request.form.get('phone')
        address=request.form.get('address')
        
        if firstname == '' or lastname == '' or username=='':
            flash('* All fields are required')
            return redirect(url_for('signup'))
        elif password != confirmpassword:
            flash('* The passwords dont match')
            return redirect('/signup/')
        elif email=='' or phone ==''or address == '':
            flash('* All fields are required')
            return redirect(url_for('signup'))
        else:
            hashed=generate_password_hash(password)
            cust=Customer(email=email,phone=phone,username=username,address=address,firstname=firstname,lastname=lastname,password=hashed)
            try:
                db.session.add(cust)
                db.session.commit()
                cust_id=cust.id  
                session['cust_id']=cust_id
                flash('Account Created Successfully')
                return redirect('/home/')
            except Exception as e:
                db.session.rollback()
                flash('This email already exist, choose another one')
                print(f"Error :{e}")
                traceback.print_exc()
                
                return redirect(url_for('signup'))
            


@app.route('/')
def home():
    
    
    # Example query for men summer wear
    men_summer_wear = Product.query.filter(Product.tags.contains('Men_summer_wear')).all()

    # Example query for latest products
    latest_products = Product.query.filter(Product.tags.contains('latest')).all()
    
    women_summer_wear = Product.query.filter(Product.tags.contains('Women summer wear')).all()

    if men_summer_wear or  latest_products:

        return render_template('user/index.html', men_summer_wear=men_summer_wear,latest_products=latest_products,women_summer_wear=women_summer_wear)
    else:
        return "No products found"

@app.route('/about/')
def about():
    return render_template('user/about.html')

@app.route('/contact/',methods=['POST','GET'])
def contact():
    return render_template('user/contact.html')



@app.route('/dashboard/')
def dashbord():
    return render_template('admin/dashboard.html')
@app.route('/user/dashboard/')
def userdashbord():
    return render_template('user/dashboard.html')




@app.route('/login/',methods=['GET','POST'])
def login():
    if  request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        check = db.session.query(Customer).filter(Customer.email==email).first()
        if check:
            hashed_password = check.password
            verify = check_password_hash(hashed_password,password)
            if verify == True:
                session['cust_id']=check.id
                return redirect('/')
            else:
                flash('*Incorrect  Password')
                return redirect('/login/')
        else:
            flash('Email not found')
            return redirect('/login/')
    else:
        return  render_template('user/login.html')
    
@app.route('/clothing/')
def clothing():
    products = Product.query.filter_by(category_id=2).all()
    return render_template('user/clothing.html',products=products)
@app.route('/accessory/')
def accessory():
    products = Product.query.filter_by(category_id=1).all()
    return render_template('user/accesory.html',products=products)

@app.route('/search/', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.form.get('search_query', '')
        
        
        # Start building the query
        query = db.session.query(Product)
        
        # Filter by search term
        if search_query:
            query = query.filter(Product.name.ilike(f'%{search_query}%') |
                                 Product.description.ilike(f'%{search_query}%'))

        
        

        # Execute query and fetch results
        results = query.all()
        
        return render_template('user/search_page.html', results=results, query=search_query)  # Show the search form

    return render_template('user/search_page.html')  
    
@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    customer_id = session.get('cust_id')
    if not customer_id:
        return redirect('/login/')

    quantity = int(request.form.get('quantity', 1))
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'status': 'error', 'message': 'Product not found'}), 404

    # Create an order if none exists for the customer
    order = Order.query.filter_by(customer_id=customer_id).first()
    if not order:
        order = Order(customer_id=customer_id, total_amount=0, status='pending')
        db.session.add(order)
        db.session.commit()

    # Add new OrderItem
    product_price = Decimal(product.price)
    new_item = OrderItem(order_id=order.id, product_id=product_id, quantity=quantity, price=product_price, amount=quantity * product_price)
    db.session.add(new_item)

    # Update order total
    order.total_amount = sum(item.amount for item in OrderItem.query.filter_by(order_id=order.id).all())
    db.session.commit()
    # Update cart count
    if 'cart_count' in session:
        session['cart_count'] += 1
    else:
        session['cart_count'] = 1
    return redirect('/view_cart/')


@app.route('/wishlist/<int:product_id>', methods=['GET', 'POST'])
def wishlist(product_id):
    # Ensure the customer is logged in
    customer_id = session.get('cust_id')
    if not customer_id:
        return jsonify({'status': 'error', 'message': 'You need to log in to add items to your wishlist.'}), 401

    # Check if the product exists
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'status': 'error', 'message': 'Product not found'}), 404

    # Get the quantity from the form, default to 1 if not provided
    quantity = request.form.get('quantity', 1)

    # Check if the product is already in the wishlist
    existing_wishlist_item = Wishlist.query.filter_by(customer_id=customer_id, product_id=product_id).first()
    if existing_wishlist_item:
        # Update the quantity of the existing wishlist item
        existing_wishlist_item.quantity += int(quantity)
    else:
        # Create a new wishlist entry
        wishlist = Wishlist(customer_id=customer_id, product_id=product_id, quantity=quantity)
        db.session.add(wishlist)

    db.session.commit()

    # Update session's wishlist count
    session['wishlist_count'] = Wishlist.query.filter_by(customer_id=customer_id).count()

    return redirect(url_for('view_wishlist'))
@app.route('/view_wishlist/')
def view_wishlist():
    if 'cust_id' not in session:
        return redirect('/login/')  # Corrected URL

    customer_id = session['cust_id']
    wishlist = Wishlist.query.filter_by(customer_id=customer_id).first()
    if not wishlist:
        return render_template('user/wishlist.html', cart_items=[], total_amount=0)

    # Join Order_item with Products to get product details
    
    
    resort_deets = db.session.query(Customer).get(customer_id)
    session['wishlist_count'] = 0
    return render_template('user/wishlist.html', resort_deets=resort_deets)


@app.route('/view_cart/')
def view_cart():
    if 'cust_id' not in session:
        return redirect('/login/')  # Corrected URL

    customer_id = session['cust_id']
    order = Order.query.filter_by(customer_id=customer_id).first()
    if not order:
        return render_template('user/cart_page.html', cart_items=[], total_amount=0)

    # Join Order_item with Products to get product details
    cart_items = (
        db.session.query(OrderItem, Product).join(Product, OrderItem.product_id == Product.id).filter(OrderItem.order_id == order.id).all()
    )
    total_amount = sum(item[0].amount for item in cart_items)
    resort_deets = db.session.query(Customer).get(customer_id)
    session['cart_count'] = 0
    return render_template('user/cart_page.html', cart_items=cart_items, total_amount=total_amount, resort_deets=resort_deets)

@app.route('/remove_from_cart/<int:product_id>/', methods=['POST'])
def remove_from_cart(product_id):
    if 'cust_id' not in session:
        return redirect('/login/')

    customer_id = session['cust_id']
    order = Order.query.filter_by(customer_id=customer_id).first()

    if order:
        item = OrderItem.query.filter_by(product_id=product_id, order_id=order.id).first()
        if item:
            try:
                db.session.delete(item)
                db.session.commit()
                order.order_total = sum(i.amount for i in OrderItem.query.filter_by(order_id=order.id).all())
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Error occurred: {e}")  
                return redirect('/') 
    return redirect('/view_cart/') 
@app.route('/payment/', methods=['GET', 'POST'])
def payment():
    if 'customer_id' not in session:
        return redirect('/login/')

    customer_id = session['cust_id']
    order = Order.query.filter_by(customer_id=customer_id).first()

    if order:
        return render_template('user/payment.html', order=order)
    else:
        return redirect('/view_cart')

@app.route('/paystack/', methods=['POST'])
def paystack():
    if 'customer_id' not in session:
        return redirect('/login/')

    customer_id = session['cust_id']
    order = Order.query.filter_by(customer_id=customer_id).first()

    if order:
        url = 'https://api.paystack.co/transaction/initialize'
        headers = {"Content-Type": "application/json", "Authorization": "Bearer YOUR_PAYSTACK_SECRET_KEY"}
        data = {"email": order.customer.email, "amount": int(order.total_amount * 100), "reference": order.id, "callback_url": "http://127.0.0.1:5000/callback/"}

        resp_json = requests.post(url, headers=headers, data=json.dumps(data))

        resp_dict = resp_json.json()

        if resp_dict and resp_dict.get('status') == True:
            auth_url = resp_dict['data']['authorization_url']
            return redirect(auth_url)
        else:
            flash('Please try again')
            return redirect('/payment/')
    else:
        return redirect('/view_cart')

@app.route('/callback/', methods=['GET'])
def callback():
    if 'customer_id' not in session:
        return redirect('/login/')

    customer_id = session['cust_id']
    order = Order.query.filter_by(customer_id=customer_id).first()

    if order:
        ref = request.args.get('reference')
        url = f"https://api.paystack.co/transaction/verify/{ref}"
        headers = {"Authorization": "Bearer YOUR_PAYSTACK_SECRET_KEY"}
        resp_json = requests.get(url, headers=headers)
        resp_dict = resp_json.json()

        if resp_dict['data']['status'] == 'success':
            order.status = 'paid'
            db.session.commit()
            flash('Payment successful')
            return redirect('/view_cart')
        else:
            order.status = 'failed'
            db.session.commit()
            flash('Payment failed')
            return redirect('/view_cart')
    else:
        return redirect('/view_cart')
    
@app.route('/profile/')
def profile():
    if 'cust_id' not in session:
        return redirect('/login/')
    else:
        customer_id = session['cust_id']
        customer = Customer.query.filter_by(id=customer_id).first()
        custorder = Order.query.filter_by(customer_id=customer_id).count()
        return render_template('user/profile.html', customer=customer,custorder=custorder)

@app.route('/logout/')
def logout():
    session.pop('cust_id')
    return redirect('/login/')
    