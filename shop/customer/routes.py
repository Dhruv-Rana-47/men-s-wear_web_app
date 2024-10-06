from flask import *

from flask_login import login_user,UserMixin,logout_user,LoginManager,login_required,current_user
from shop.app import web,db,User,mail_sr
import re
from shop.product.models import *
from .models import Order,OrderDetail,Cart,Profile
from flask import jsonify
from werkzeug.utils import secure_filename
import os
from flask_mail import *
from random import randint
# from shop import config

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Function to check if a filename has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# session=Session()
# session['order_placed']=False


def generate_ord_id():
    # Query the last order ID from the database
    last_order = Order.query.order_by(Order.ord_id.desc()).first()

    # If there are no orders in the database, start with 101
    if not last_order:
        return 'ord101'

    # Extract the numeric part of the last order ID
    last_ord_id_numeric = int(last_order.ord_id[3:])

    # Generate the next order ID by incrementing the numeric part
    next_ord_id_numeric = last_ord_id_numeric + 1

    # Construct the next order ID with the incremented numeric part
    next_ord_id = f'ord{next_ord_id_numeric}'

    return next_ord_id







@web.context_processor
def inject_categories():
    # Fetch your categories data from wherever it's stored
    categories = Category.query.all()
    return dict(categories=categories)

@web.route('/')
def home():
    categories = Category.query.all() 
    return render_template("home.html")


@web.route('/profile',methods=['GET','POST'])
def profile():
    user_id=current_user.id
    prof=Profile.query.get(user_id)
    return render_template("customer/profile.html",profile=prof)


@web.route('/update_profile',methods=['GET','POST'])
def upd_profile():
    user_id=current_user.id
    user = User.query.filter_by(id=user_id).first()
    profile= Profile.query.filter_by(user_id=user_id).first()
    return render_template("customer/profile_form.html",user=user,profile=profile)


@web.route('/submit_profile', methods=['POST'])
def submit_profile():
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            address = request.form['address']
            dob = request.form['dob']
            age = request.form['age']
            gender = request.form['gender']
            user_id=current_user.id
            profile_pic = request.files['profile_photo']
            if profile_pic and allowed_file(profile_pic.filename):
                profile_pic.save(os.path.join(web.config['UPLOAD_FOLDER'],profile_pic.filename))
                

            prof_pic=(os.path.join(web.config['UPLOAD_FOLDER'],profile_pic.filename))
            print("Entering data fetch block")
            prof=Profile.query.get(user_id)
        # If the user doesn't have a profile yet, create a new one
            if not prof:
                print("Entering if block")
                new_profile = Profile(user_id=user_id, address=address, date_of_birth=dob, age=age, gender=gender,profile_pic=prof_pic)
                db.session.add(new_profile)
            else:
                try:
                    print("Entering else block")
                    prof.profile_pic=prof_pic
                    prof.address = address
                    prof.date_of_birth = dob
                    prof.age = age
                    prof.gender = gender
                except Exception as e:
                    print("Error updating profile:", e)
                    db.session.rollback()


        db.session.commit()
        return redirect("/profile")

@web.route('/login',methods=['GET','POST'])
def login():
     if request.method=='POST':
         mail=request.form.get('uname')
         password =request.form.get("psw")
         user=User.query.filter_by(email=mail).first()
         if user and user.chpsw(password):
             login_user(user)
             if 'pending_cart' in session:
                pending_items = session['pending_cart']

        # Iterate over each pending item and add it to the user's cart
                for item in pending_items:
                    pro_id = item['product_id']
                    quantity = item['quantity']

                    # Add the pending item to the cart
                    cart = Cart(user_id=current_user.id, product_id=pro_id, quantity=quantity)
                    db.session.add(cart)

        # Commit changes to the database
                db.session.commit()

        # Clear pending cart data from session
                session.pop('pending_cart')

             if current_user.id ==1:
                    return redirect('/myadmin')
             else:
                 next_url = session.get('next_url')
                 if next_url:
                    session.pop('next_url')  # Clear stored URL from session
                    return redirect(next_url)  # Redirect to the stored URL
                 else:
                     return render_template("home.html")
            
         else:
             flash('incorrect email or passwords',"error")
             return render_template("customer/login.html")
     else:
         flash("please login first,or if you dont have account sign-Up or create Your account","info")
         session['next_url'] = request.referrer
         return render_template("customer/login.html")
            

@web.route('/register',methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        uname = request.form.get("name")
        mail = request.form.get("email")
        password = request.form.get("psw")

        # Email pattern regex
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

        # Minimum password length
        min_password_length = 6
        username_pattern = r'^[a-zA-Z\s]+$'
        # Check if email matches the pattern
        if not re.match(email_pattern, mail):
            flash("Invalid email address format", 'error')
            return render_template("customer/login.html")

        # Check if password meets minimum length and contains at least one number
        if len(password) < min_password_length or not any(char.isdigit() for char in password):
            flash("Password must be at least 6 characters long and contain at least one number", 'error')
            return render_template("customer/login.html")
        
        if not re.match(username_pattern, uname):
            flash("Username must contain only alphabets and spaces", 'error')
            return render_template("customer/login.html")
        
        session['uname']=uname
        session['mail']=mail
        session['password']=password

        return redirect('/verify')
        
    else:
        flash(" if you dont have account sign-Up or create Your account","info")
        return render_template("customer/login.html")
     
@web.route('/verify',methods=['GET','POST'])
def verify():
    if request.method=='POST':
        user_otp=request.form.get('otp')
        user_otp = int(user_otp) 
        stored_otp = session.get('otp')
        if stored_otp is not None and isinstance(stored_otp, int):
            if user_otp == stored_otp:
                uname=session.get('uname')
                mail=session.get('mail')
                password=session.get('password')
                session.pop('uname', None)
                session.pop('mail', None)
                session.pop('password', None)
                session.pop('otp',None) 
                existing_user= User.query.all()
                if existing_user:
                    new_id = max(user.id for user in existing_user) + 1
        # If there are records, fetch the maximum ID and increment it by 1
                else:
                    new_id =2
            # If user submitted the data then it will check this if block and store details to the database
            
                new_user = User(id=new_id,name=uname, email=mail, password=password)
                new_pro=Profile(user_id=new_id)
                try:
                    db.session.add(new_user)
                    db.session.add(new_pro)
                    db.session.commit()
                    # After storing data form redirected to the login page
                    user=User.query.filter_by(email=mail).first()
                    login_user(user)
                    return render_template("home.html")
                except Exception as e:
                    flash("Email already exists, use another email", 'error')
                    return render_template("customer/login.html")
            else:
                return redirect('/verify')
        else:
            flash("some technical error!", 'info')
            return render_template("customer/otp.html")

    else:
        email=session.get('mail')
        otp=randint(0000,9999)
        session['otp']=otp
        msg=Message('verification code',sender='managerrana47@gmail.com',recipients=[email])
        msg.body="your otp code is:"+"\n"+str(otp)
        mail_sr.send(msg)
        flash("please enter otp sent on your Register email!", 'info')
        return render_template("customer/otp.html")
    
      
@web.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


# @web.route('/succ')
# def succ():

#     return render_template("customer/succ.html")

@web.route('/sub_cat/<int:cat_id>',methods=['GET','POST'])
def sub_cat(cat_id):
    cat = Category.query.get(cat_id)
    subcategories = cat.subcategories
    return render_template("product/sub_cat.html",cat=cat,subcat=subcategories)


@web.route('/products/<int:sub_id>',methods=['GET','POST'])
@login_required
def product_dis(sub_id):
    subcat = Subcategory.query.get(sub_id)
    products = subcat.products
    return render_template("product/products.html",products=products,subcat=subcat)



@web.route('/one_pro/<int:pro_id>',methods=['GET','POST'])
def product(pro_id):
    pro = Product.query.get(pro_id)
    return render_template("product/single-product.html",pro=pro)


@web.route('/addcart/<int:pro_id>',methods=['GET','POST'])
def add_cart(pro_id):
    product = Product.query.get(pro_id)
    quantity = request.form.get('quantity', default=1, type=int)

    # If the user is logged in, add the product to the cart
    if current_user.is_authenticated:
        cart = Cart(user_id=current_user.id, product_id=pro_id, quantity=quantity)
        db.session.add(cart)
        db.session.commit()
        return redirect(request.referrer)
    else:
        if 'pending_cart' not in session:
            session['pending_cart'] = []

    # Append the new product data to the pending cart list
            session['pending_cart'].append({'product_id': pro_id, 'quantity': quantity})

    return redirect(request.referrer)
    # Check if referrer exists and is not the same as the current URL to prevent redirection loop
    # if referrer and referrer != request.url:
    #     return redirect(referrer)
    # else:
    #     # If referrer is not available or is the same as the current URL, redirect to a default URL
    #     return redirect('/')



@web.route('/cart',methods=['GET','POST'])
def cart():
    if current_user.is_authenticated:
        # Query cart items for the logged-in user
        cart_rows = Cart.query.filter(Cart.user_id == current_user.id).all()
        return render_template("customer/cart.html", cart=cart_rows)
    else:
        # If the user is not logged in, redirect them to the login page
        return redirect('/login')


    

@web.route('/del_cart/<int:cart_id>', methods=['POST','GET'])
@login_required
def delete_cart_item(cart_id):
    cart_item = Cart.query.get_or_404(cart_id)
    db.session.delete(cart_item)
    db.session.commit()
    total_cart_price = 0 

    return redirect(url_for('cart', cus_id=cart_item.user_id))
    


@web.route('/update_cart_quantity/<int:cart_id>', methods=['POST'])
def update_cart_quantity(cart_id):
    if request.method == 'POST':
        new_quantity = request.json.get('quantity')
        if new_quantity is not None:
            # Update the cart quantity in the database
            cart = Cart.query.get_or_404(cart_id)
            cart.quantity = new_quantity
            db.session.commit()
            return jsonify({'message': 'Cart quantity updated successfully'}), 200
        else:
            return jsonify({'error': 'Invalid request'}), 400
    else:
        return jsonify({'error': 'Method not allowed'}), 405

    
@web.route('/order_info', methods=['POST','GET'])
@login_required
def order_info():
    if request.method == 'POST':
        # Extract data from the form
        name = request.form['name']
        email = request.form['email']
        telephone = request.form['telephone']
        city = request.form['city']
        pincode = request.form['pincode']
        address = request.form['address']
        payment_method = 'cod'



        
        if payment_method == 'upi':
            pass
             # Execute specific code for UPI payment method
               # For example:
        # Process UPI payment...
        else:
            new_ord_id = generate_ord_id()
        # Create an instance of the Order model and populate it with the form data
            order = Order(ord_id=new_ord_id,cus_name=name, telephone=telephone, ord_city=city, pincode=pincode, shipping_address=address, user_id=current_user.id,status='confirmed',payment_type=payment_method)
            db.session.add(order)
            cart_items = Cart.query.filter_by(user_id=current_user.id).all()

        # Iterate over cart items to create order details and delete them from the cart
            for cart_item in cart_items:
                order_detail = OrderDetail(ord_id=new_ord_id, product_id=cart_item.product_id, quantity=cart_item.quantity)
                db.session.add(order_detail)
                db.session.delete(cart_item)
           # Add the order to the database session
            db.session.commit()
            # session['order_placed'] = True
            
            msg = "Mens Monologue want to inform you that..."+"\n" +"Your order has been placed successfully."
            additional_data = "Order ID: " + new_ord_id  + "\nUser: " + name
            final_msg = msg + "\n" + additional_data

            msgs=Message(sender='managerrana47@gmail.com',recipients=[email],subject='Order Confirmed',body=final_msg)
            mail_sr.send(msgs)
            flash("Your order has been placed successfully!", 'success')
            return redirect('/')
            
        # return redirect(url_for('cart', cus_id=user_id))  # Redirect to the cart page after processing the order
       
    else:
        return render_template("customer/order_info.html")
  

@web.route('/orders')
@login_required
def order():
    cus_id=current_user.id
    orders=Order.query.filter(Order.user_id == cus_id).all()

    return render_template("customer/order_history.html",orders=orders)

import pdfkit


@web.route('/billpdf')
def pdf():
     cus_id=current_user.id
     latest_order = Order.query.filter(Order.user_id == cus_id).order_by(desc(Order.ord_date)).first()

     rendered= render_template("customer/invoice_pdf.html",order=latest_order)
            # pdf=pdfkit.from_string(rendered,False).from_file('input.html', 'output.pdf', configuration=config)
            # Write the rendered HTML to a temporary file
     with open('temp_invoice.html', 'w',encoding='utf-8') as f:
        f.write(rendered)
     config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

            # Generate PDF from the HTML file
     pdf_output_path = 'invoice.pdf'
     pdfkit.from_file('temp_invoice.html', pdf_output_path, configuration=config)
     response = make_response(open(pdf_output_path, 'rb').read())
     response.headers['Content-Type'] = 'application/pdf'
     response.headers['Content-Disposition'] = 'inline: filename=invoice.pdf'
     os.remove('temp_invoice.html')
     os.remove(pdf_output_path)
     return response
     referrer = request.referrer    
     if referrer and referrer != request.url:
        redirect(referrer)

@web.route('/contact')
@login_required
def contact():
    return render_template("contact.html")

from sqlalchemy import desc
@web.route('/neworder')
@login_required
def neword():
    cus_id=current_user.id
    latest_order = Order.query.filter(Order.user_id == cus_id).order_by(desc(Order.ord_date)).first()
    return render_template("customer/last-order.html",order=latest_order)




@web.route('/chg_pswd', methods=['GET', 'POST'])
def change_pswd():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        if new_password != confirm_password:
            flash('New password and confirm password do not match.', 'error')
            return redirect(url_for('change_password'))

        user = User.query.filter_by(email=current_user.email).first()  # Replace 'example_username' with actual username
        if user and user.chpsw(current_password):
            user.password = user.hash_password(new_password)
            db.session.commit()
            flash('Password updated successfully.', 'success')
            return  render_template('customer/chg_pswd.html')
        else:
            flash('Incorrect current password.', 'error')
            return redirect(url_for('change_pswd'))

    return render_template('customer/chg_pswd.html')