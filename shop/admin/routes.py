from flask import *
from flask_login import login_user,UserMixin,logout_user,LoginManager,login_required,current_user
from shop.app import web,db,User
from shop.product.models import Category,Subcategory,Product,Size,Color
from shop.customer.models import Order,OrderDetail,Cart
from sqlalchemy import func,and_
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.exc import IntegrityError

import pdfkit

# Define the configuration with the path to wkhtmltopdf executable

# Use the configuration when generating PDF from file



@web.route('/myadmin',methods=['Get','post'])
@login_required
def admin_panel():
    if current_user.id == 1 and current_user.is_authenticated:   
        # Render your admin panel template or redirect to the admin panel
        product_count = db.session.query(Product).count()
        cat_count = db.session.query(Category).count()
        sub_count = db.session.query(Subcategory).count()
        user_count = db.session.query(User).count()
        order_count=db.session.query(Order).count()
        total_sales = db.session.query(func.sum(OrderDetail.quantity * Product.price)).\
           join(OrderDetail.product).\
           join(Order).scalar()



        return render_template('admin/dashboard.html',prod_cnt=product_count,cat_cnt=cat_count,sub_cnt=sub_count,user_cnt=user_count,order_cnt=order_count,revenue=total_sales)
    else:
        # Redirect to a page indicating unauthorized access
        return redirect(url_for('unauthorized'))

@web.route('/unauthorized')
def unauthorized():
    # Render a template indicating unauthorized access
    return render_template('unauthorized.html')


@web.route('/user',methods=['Get','post'])
@login_required
def user():   
    if current_user.id == 1 and current_user.is_authenticated:
        users = User.query.all()  # Fetch all category items from the database
        return render_template("admin/user/userlist.html", users=users)


#remaining user,dit add and delete routes->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>





@web.route('/category',methods=['Get','post'])
@login_required
def cat():
    if current_user.id == 1 and current_user.is_authenticated:
        categories = Category.query.all()  # Fetch all category items from the database
        return render_template("admin/category/cat_panel.html", categories=categories)



@web.route('/addcat',methods=['Get','post'])
@login_required
def add_cat():
    if current_user.id == 1 and current_user.is_authenticated:
        if request.method=='POST':
            existing_categories = Category.query.all()
            if existing_categories:
                new_id = max(category.cid for category in existing_categories) + 1
        # If there are records, fetch the maximum ID and increment it by 1
            else:
                new_id = 1

        # If there are no records, set the new ID as 1
            cname=request.form.get("cname")
            new_cat=Category(cname=cname,cid=new_id)
            db.session.add(new_cat)
            db.session.commit()
            cat=Category.query.filter_by(cid=new_id).first()
            flash(f' {cat.cname}  is successfully added to the database',"success")
            return redirect("/category")
            
        else:
            return render_template("admin/category/addcat.html")
    else:
        return redirect(url_for('unauthorized'))




@web.route('/delete/<int:category_id>', methods=['GET', 'POST'])
@login_required
def delete_category(category_id):
    if current_user.id == 1 and current_user.is_authenticated:
        category = Category.query.get(category_id)
        if category:
            try:
                db.session.delete(category)
                db.session.commit()
                flash(f'Category "{category.cname}" deleted successfully', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Failed to delete category "{category.cname}"', 'danger')
        else:
            flash('Category not found', 'danger')

        return redirect('/category')
    else:
        return redirect(url_for('unauthorized'))


@web.route('/delete_selected_categories', methods=['POST'])
@login_required
def delete_selected_categories():
    if current_user.id == 1 and current_user.is_authenticated:

        if request.method == 'POST':
            if 'delete_selected' in request.form:
                selected_category_ids = request.form.getlist('selected_categories[]')
                
                for category_id in selected_category_ids:
                    category = Category.query.get(category_id)
                    if category:
                        db.session.delete(category)

                db.session.commit()
                flash('Selected categories deleted successfully', 'success')
                return redirect('/category') 
            

        # Redirect to the category page after deletion or addition
    else:
        return redirect(url_for('unauthorized'))


@web.route('/edit_category/<int:category_id>', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    if current_user.id == 1 and current_user.is_authenticated:

        category = Category.query.get(category_id)
        if not category:
            # Handle case where category with the provided ID does not exist
            return "Category not found", 404
        
        if request.method == 'POST':
            # Update category data based on form submission
            category.cname = request.form['cname']
            # Add additional fields as needed
            
            # Commit changes to the database
            db.session.commit()
            flash('categories name updated successfully', 'success')
            # Redirect to category list page after successful edit
            return redirect('/category')
        else:
            # Render the edit form with pre-filled data
            return render_template('admin/category/editcat.html', category=category)
    else:
        return redirect(url_for('unauthorized'))

# category routes ended<-<-<-----<
    
# sub category routes->->->>->>



@web.route('/subcat',methods=['Get','post'])
@login_required
def subcat():
    if current_user.id == 1 and current_user.is_authenticated:
  
        subcategories = Subcategory.query.all()  # Fetch all category items from the database
        
        return render_template("admin/subcat/sub_panel.html", subcategories=subcategories)
    else:
        return redirect(url_for('unauthorized'))



@web.route('/addsub',methods=['Get','post'])
@login_required
def add_sub():
    if current_user.id == 1 and current_user.is_authenticated:

     
        if request.method=='POST':
            existing_subcat = Subcategory.query.all()
            if existing_subcat:
                new_id = max(subcategory.sub_id for subcategory in existing_subcat) + 1
            # If there are records, fetch the maximum ID and increment it by 1
            else:
                new_id = 101

            # If there are no records, set the new ID as 1
            sub_name=request.form.get("subname")
            cid=request.form.get("cid")
            new_cat=Subcategory(sub_name=sub_name,sub_id=new_id,cid=cid)
            db.session.add(new_cat)
            db.session.commit()
            subcat=Subcategory.query.filter_by(sub_id=new_id).first()
            flash(f' {subcat.sub_name}  is successfully added to the database',"success")
            return redirect("/subcat")
                
        else:
            existing_categories = Category.query.all()
            return render_template("admin/subcat/addsub.html",categories=existing_categories)
    else:
        return redirect(url_for('unauthorized'))




@web.route('/delete_sub/<int:subcategory_id>', methods=['GET', 'POST'])
@login_required
def delete_subcat(subcategory_id):
    if current_user.id == 1 and current_user.is_authenticated:


        subcategory = Subcategory.query.get(subcategory_id)
        if subcategory:
            try:
                db.session.delete(subcategory)
                db.session.commit()
                flash(f'subCategory "{subcategory.sub_name}" deleted successfully', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Failed to delete sub category "{subcategory.sub_name}"', 'danger')
        else:
            flash('sub_Category not found', 'danger')

        return redirect('/subcat')
    else:
        return redirect(url_for('unauthorized'))

@web.route('/delete_selected_subcat', methods=['POST'])
@login_required
def delete_selected_subcat():
    if current_user.id == 1 and current_user.is_authenticated:

        if request.method == 'POST':
            if 'delete_selected' in request.form:
                selected_subcategories_ids = request.form.getlist('selected_subcategories[]')
                
                for subcat_id in selected_subcategories_ids:
                    subcategory = Subcategory.query.get(subcat_id)
                    if subcategory:
                        db.session.delete(subcategory)

                db.session.commit()
                flash('Selected subcategories deleted successfully', 'success')
                return redirect('/subcat') 
    else:
        return redirect(url_for('unauthorized'))    

     

@web.route('/edit_sub/<int:subcat_id>', methods=['GET', 'POST'])
@login_required
def edit_sub(subcat_id):
    if current_user.id == 1 and current_user.is_authenticated:

        subcategory = Subcategory.query.get(subcat_id)
        
        if not subcategory:
            # Handle case where category with the provided ID does not exist
            return "subCategory not found", 404
        
        if request.method == 'POST':
            # Update category data based on form submission
            subcategory.sub_name = request.form['sub_name']
            # Add additional fields as needed
            
            # Commit changes to the database
            db.session.commit()
            flash('subcategories name updated successfully', 'success')
            # Redirect to category list page after successful edit
            return redirect('/subcat')
        else:
            # Render the edit form with pre-filled data
            return render_template('admin/subcat/editsub.html', subcategory=subcategory)





from shop.product import routes

             
@web.route('/color',methods=['Get','post'])
@login_required
def clr():
    if current_user.id == 1 and current_user.is_authenticated:

        colors = Color.query.all()  # Fetch all category items from the database
        return render_template("admin/color/color_panel.html", colors=colors)



@web.route('/addclr',methods=['Get','post'])
@login_required
def add_clr():
    if current_user.id == 1 and current_user.is_authenticated:

        if request.method=='POST':
            existing_clr = Color.query.all()
            if existing_clr:
                new_id = max(clr.color_id for clr in existing_clr) + 1
            # If there are records, fetch the maximum ID and increment it by 1
            else:
                new_id = 1

            # If there are no records, set the new ID as 1
            cname=request.form.get("cname")
            new_clr=Color(name=cname,color_id=new_id)
            db.session.add(new_clr)
            db.session.commit()
            clr=Color.query.filter_by(color_id=new_id).first()
            flash(f' {clr.name}  is successfully added to the database',"success")
            return redirect("/color")
                
        else:
            return render_template("admin/color/addclr.html")



@web.route('/delete_clr/<int:clr_id>', methods=['GET', 'POST'])
@login_required
def delete_clr(clr_id):
    if current_user.id == 1 and current_user.is_authenticated:


        clr = Color.query.get(clr_id)
        if clr:
            try:
                db.session.delete(clr)
                db.session.commit()
                flash(f'Color "{clr.name}" deleted successfully', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Failed to delete color "{clr.name}"', 'danger')
        else:
            flash('Color not found', 'danger')

        return redirect('/color')

@web.route('/delete_selected_clr', methods=['POST'])
@login_required
def delete_selected_clr():
    if current_user.id == 1 and current_user.is_authenticated:

        if request.method == 'POST':
            if 'delete_selected' in request.form:
                selected_category_ids = request.form.getlist('selected_colors[]')
                
                for clr_id in selected_category_ids:
                    clr = Color.query.get(clr_id)
                    if clr:
                        db.session.delete(clr)

                db.session.commit()
                flash('Selected Colors deleted successfully', 'success')
                return redirect('/Color') 
            

     # Redirect to the category page after deletion or addition

@web.route('/edit_clr/<int:clr_id>', methods=['GET', 'POST'])
@login_required
def edit_clr(clr_id):
    if current_user.id == 1 and current_user.is_authenticated:
    
        clr = Color.query.get(clr_id)
        if not clr:
            # Handle case where category with the provided ID does not exist
            return "Color not found", 404
        
        if request.method == 'POST':
            # Update category data based on form submission
            clr.name = request.form['cname']
            # Add additional fields as needed
            
            # Commit changes to the database
            db.session.commit()
            flash('Color name updated successfully', 'success')
            # Redirect to category list page after successful edit
            return redirect('/color')
        else:
            # Render the edit form with pre-filled data
            return render_template('admin/color/editclr.html', clr=clr)
        

# size routes start->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.

            
@web.route('/size',methods=['Get','post'])
@login_required
def size():
    if current_user.id == 1 and current_user.is_authenticated:
    
        sizes = Size.query.all()  # Fetch all category items from the database
        return render_template("admin/size/size_panel.html", sizes=sizes)



@web.route('/addsize',methods=['Get','post'])
@login_required
def add_size():
    if current_user.id == 1 and current_user.is_authenticated:
    
        if request.method=='POST':
            existing_size = Size.query.all()
            if existing_size:
                new_id = max(sz.sid for sz in existing_size) + 1
            # If there are records, fetch the maximum ID and increment it by 1
            else:
                new_id = 1

            # If there are no records, set the new ID as 1
            sname=request.form.get("sname")
            new_sz=Size(name=sname,sid=new_id)
            db.session.add(new_sz)
            db.session.commit()
            sz=Size.query.filter_by(sid=new_id).first()
            flash(f' {sz.name}  is successfully added to the database',"success")
            return redirect("/size")
                
        else:
            return render_template("admin/size/addsize.html")



@web.route('/delete_size/<int:sz_id>', methods=['GET', 'POST'])
@login_required
def delete_sz(sz_id):
    if current_user.id == 1 and current_user.is_authenticated:
    
        sz = Size.query.get(sz_id)
        if sz:
            try:
                db.session.delete(sz)
                db.session.commit()
                flash(f'Size "{sz.name}" deleted successfully', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Failed to delete size"{sz.name}"', 'danger')
        else:
            flash('size not found', 'danger')

        return redirect('/size')

@web.route('/delete_selected_size', methods=['POST'])
@login_required
def delete_selected_sz():
    if current_user.id == 1 and current_user.is_authenticated:
    
        if request.method == 'POST':
            if 'delete_selected' in request.form:
                selected_category_ids = request.form.getlist('selected_size[]')
                
                for sz_id in selected_category_ids:
                    sz = Size.query.get(sz_id)
                    if sz:
                        db.session.delete(sz)

                db.session.commit()
                flash('Selected size deleted successfully', 'success')
                return redirect('/size') 
        

     # Redirect to the category page after deletion or addition

@web.route('/edit_size/<int:sz_id>', methods=['GET', 'POST'])
@login_required
def edit_sz(sz_id):
    if current_user.id == 1 and current_user.is_authenticated:
    
        sz = Size.query.get(sz_id)
        if not sz:
            # Handle case where category with the provided ID does not exist
            return "Color not found", 404
        
        if request.method == 'POST':
            # Update category data based on form submission
            sz.name = request.form['sname']
            # Add additional fields as needed
            
            # Commit changes to the database
            db.session.commit()
            flash('size name updated successfully', 'success')
            # Redirect to category list page after successful edit
            return redirect('/size')
        else:
            # Render the edit form with pre-filled data
            return render_template('admin/size/editsize.html', size=sz)

           
@web.route('/order',methods=['GET','POST'])
@login_required
def order_tb():
    if current_user.id == 1 and current_user.is_authenticated:
        
        order = Order.query.all()  # Fetch all category items from the database
        return render_template("admin/order/order_panel.html", order=order)

           
@web.route('/order_detail',methods=['GET','POST'])
@login_required
def order_det_tb():
    if current_user.id == 1 and current_user.is_authenticated:
    
        ord = OrderDetail.query.all()  # Fetch all category items from the database
        return render_template("admin/order/order_det_pan.html", order_det=ord)
    

@web.route('/report',methods=['GET','POST'])
@login_required
def report():
    if current_user.id == 1 and current_user.is_authenticated:
        if request.method == 'POST':
        # Get start and end date from request arguments
            start_date_str = request.form.get('start_date')
            end_date_str = request.form.get('end_date')
            
            # Convert start and end date strings to datetime objects
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

            # Query orders within the specified date range
            orders_within_range = db.session.query(Order).filter(Order.ord_date.between(start_date, end_date)).all()

            # Initialize dictionary to store order details
            sales_report = []

            # Iterate over orders
            for order in orders_within_range:
                order_details = {
                    'Order ID': order.ord_id,
                    'Order Date': order.ord_date,
                    'Customer Name': order.cus_name,
                    'Total Amount': 0,  # Initialize total amount for the order
                    'Status': order.status,
                    'Shipping Address': order.shipping_address,
                    'Payment Type': order.payment_type,
                    'Telephone': order.telephone,
                    'Number of Items': 0  # Initialize total number of items for the order
                }

                # Iterate over order details to calculate total amount and number of items
                for order_detail in order.order_details:
                    product = order_detail.product
                    product_total = order_detail.quantity * product.price
                    order_details['Total Amount'] += product_total
                    order_details['Number of Items'] += order_detail.quantity

                    # Add product details to the order details
                    order_details[f'Product {product.pid}'] = {
                        'Product Name': product.pname,
                        'Quantity': order_detail.quantity,
                        'Price Per Unit': product.price,
                        'Total Price': product_total
                    }

                # Add order details to the sales report
                sales_report.append(order_details)

            # Calculate total sales within the specified date range
            total_sales = db.session.query(func.sum(OrderDetail.quantity * Product.price)).\
                join(OrderDetail.product).\
                join(Order).\
                filter(Order.ord_date.between(start_date, end_date)).scalar()

            # Render the sales report template with the retrieved data
            return render_template('admin/report/sale_report.html', sales_report=sales_report, total_sales=total_sales)
        else:
            # If the request method is not POST, render the page without data
            return render_template('admin/report/sale_report.html', sales_report=None, total_sales=None)
    else:
        return redirect(url_for('unauthorized'))




from flask import make_response
import os

@web.route('/gen_pdf',methods=['GET','POST'])
@login_required
def gen_pdf():
    if current_user.id == 1 and current_user.is_authenticated:
        if request.method == 'POST':
        # Get start and end date from request arguments
            start_date_str = request.form.get('start_date')
            end_date_str = request.form.get('end_date')
            
            # Convert start and end date strings to datetime objects
            try:
                # Convert start and end date strings to datetime objects
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            except ValueError as e:
                 # Handle the case where the date strings are not in the expected format or are empty
                error_message = "Invalid date format. Please enter dates in YYYY-MM-DD format."
                return render_template('error.html', error_message=error_message)
            # Query orders within the specified date range
            orders_within_range = db.session.query(Order).filter(Order.ord_date.between(start_date, end_date)).all()

            # Initialize dictionary to store order details
            sales_report = []

            # Iterate over orders
            for order in orders_within_range:
                order_details = {
                    'Order ID': order.ord_id,
                    'Order Date': order.ord_date,
                    'Customer Name': order.cus_name,
                    'Total Amount': 0,  # Initialize total amount for the order
                    'Status': order.status,
                    'Shipping Address': order.shipping_address,
                    'Payment Type': order.payment_type,
                    'Telephone': order.telephone,
                    'Number of Items': 0  # Initialize total number of items for the order
                }

                # Iterate over order details to calculate total amount and number of items
                for order_detail in order.order_details:
                    product = order_detail.product
                    product_total = order_detail.quantity * product.price
                    order_details['Total Amount'] += product_total
                    order_details['Number of Items'] += order_detail.quantity

                    # Add product details to the order details
                    order_details[f'Product {product.pid}'] = {
                        'Product Name': product.pname,
                        'Quantity': order_detail.quantity,
                        'Price Per Unit': product.price,
                        'Total Price': product_total
                    }

                # Add order details to the sales report
                sales_report.append(order_details)

            # Calculate total sales within the specified date range
            total_sales = db.session.query(func.sum(OrderDetail.quantity * Product.price)).\
                join(OrderDetail.product).\
                join(Order).\
                filter(Order.ord_date.between(start_date, end_date)).scalar()

            # Render the sales report template with the retrieved data
           
            rendered= render_template('admin/report/report_pdf.html', sales_report=sales_report, total_sales=total_sales,from_date=start_date_str,to_date=end_date_str)
            # pdf=pdfkit.from_string(rendered,False).from_file('input.html', 'output.pdf', configuration=config)
            # Write the rendered HTML to a temporary file
            with open('temp_report.html', 'w',encoding='utf-8') as f:
                f.write(rendered)

            # Define PDF configuration
            config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

            # Generate PDF from the HTML file
            pdf_output_path = 'sales_report.pdf'
            pdfkit.from_file('temp_report.html', pdf_output_path, configuration=config)

            # Send the generated PDF file as a response
            response = make_response(open(pdf_output_path, 'rb').read())
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = 'inline; filename=sales_report.pdf'
            os.remove('temp_report.html')
            os.remove(pdf_output_path)
            return response
       # Check if referrer exists and is not the same as the current URL to prevent redirection loop
    referrer = request.referrer    
    if referrer and referrer != request.url:
        redirect(referrer)



@web.route('/cat_report',methods=['GET','POST'])
@login_required
def cat_report():
    if current_user.id == 1 and current_user.is_authenticated:
        categories = Category.query.all()
        if request.method == 'POST':
            start_date_str = request.form.get('start_date')
            end_date_str = request.form.get('end_date')
            
            # Convert start and end date strings to datetime objects
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            category_id = request.form.get('category-filter')  

            orders_within_range = db.session.query(Order) \
                .join(OrderDetail, Order.ord_id == OrderDetail.ord_id) \
                .join(Product, OrderDetail.product_id == Product.pid) \
                .filter(and_(Order.ord_date.between(start_date, end_date),
                            Product.cid == category_id)) \
                .all()
            # Query orders within the specified date range
            

            # Initialize dictionary to store order details
            sales_report = []

            # Iterate over orders
            for order in orders_within_range:
                order_details = {
                    'Order ID': order.ord_id,
                    'Order Date': order.ord_date,
                    'Customer Name': order.cus_name,
                    'Total Amount': 0,  # Initialize total amount for the order
                    'Status': order.status,
                    'Shipping Address': order.shipping_address,
                    'Payment Type': order.payment_type,
                    'Telephone': order.telephone,
                    'Number of Items': 0  # Initialize total number of items for the order
                }

                # Iterate over order details to calculate total amount and number of items
                for order_detail in order.order_details:
                    product = order_detail.product
                    product_total = order_detail.quantity * product.price
                    order_details['Total Amount'] += product_total
                    order_details['Number of Items'] += order_detail.quantity

                    # Add product details to the order details
                    order_details[f'Product {product.pid}'] = {
                        'Product Name': product.pname,
                        'Quantity': order_detail.quantity,
                        'Price Per Unit': product.price,
                        'Total Price': product_total
                    }

                # Add order details to the sales report
                sales_report.append(order_details)

            # Calculate total sales within the specified date range
            total_sales = db.session.query(func.sum(OrderDetail.quantity * Product.price)).\
                join(OrderDetail.product).\
                join(Order).\
                filter(Order.ord_date.between(start_date, end_date)).\
                filter(OrderDetail.product.has(cid=category_id)).scalar()
            
            return render_template('admin/report/cate_report.html', sales_report=sales_report, total_sales=total_sales,cat=categories)
            
        else:
            return render_template("admin/report/cate_report.html",sales_report=None, total_sales=None,cat=categories)


@web.route('/gen_catpdf',methods=['GET','POST'])
@login_required
def gen_catpdf():
    if current_user.id == 1 and current_user.is_authenticated:
        if request.method == 'POST':
        # Get start and end date from request arguments
            start_date_str = request.form.get('start_date')
            end_date_str = request.form.get('end_date')
            category_id = request.form.get('cat')

            cat=Category.query.get(category_id)
            
            # Convert start and end date strings to datetime objects
            try:
                # Convert start and end date strings to datetime objects
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            except ValueError as e:
                 # Handle the case where the date strings are not in the expected format or are empty
                error_message = "Invalid date format. Please enter dates in YYYY-MM-DD format."
                return render_template('error.html', error_message=error_message)
            # Query orders within the specified date range
            orders_within_range = db.session.query(Order) \
                .join(OrderDetail, Order.ord_id == OrderDetail.ord_id) \
                .join(Product, OrderDetail.product_id == Product.pid) \
                .filter(and_(Order.ord_date.between(start_date, end_date),
                            Product.cid == category_id)) \
                .all()
            # Query orders within the specified date range
            

            # Initialize dictionary to store order details
            sales_report = []

            # Iterate over orders
            for order in orders_within_range:
                order_details = {
                    'Order ID': order.ord_id,
                    'Order Date': order.ord_date,
                    'Customer Name': order.cus_name,
                    'Total Amount': 0,  # Initialize total amount for the order
                    'Status': order.status,
                    'Shipping Address': order.shipping_address,
                    'Payment Type': order.payment_type,
                    'Telephone': order.telephone,
                    'Number of Items': 0  # Initialize total number of items for the order
                }

                # Iterate over order details to calculate total amount and number of items
                for order_detail in order.order_details:
                    product = order_detail.product
                    product_total = order_detail.quantity * product.price
                    order_details['Total Amount'] += product_total
                    order_details['Number of Items'] += order_detail.quantity

                    # Add product details to the order details
                    order_details[f'Product {product.pid}'] = {
                        'Product Name': product.pname,
                        'Quantity': order_detail.quantity,
                        'Price Per Unit': product.price,
                        'Total Price': product_total
                    }

                # Add order details to the sales report
                sales_report.append(order_details)

            # Calculate total sales within the specified date range
            total_sales = db.session.query(func.sum(OrderDetail.quantity * Product.price)).\
                join(OrderDetail.product).\
                join(Order).\
                filter(Order.ord_date.between(start_date, end_date)).\
                filter(OrderDetail.product.has(cid=category_id)).scalar()
            
            
            rendered= render_template('admin/report/cate_report_pdf.html', sales_report=sales_report, total_sales=total_sales,from_date=start_date_str,to_date=end_date_str,cat=cat)
            # pdf=pdfkit.from_string(rendered,False).from_file('input.html', 'output.pdf', configuration=config)
            # Write the rendered HTML to a temporary file
            with open('temp_report.html', 'w',encoding='utf-8') as f:
                f.write(rendered)

            # Define PDF configuration
            config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

            # Generate PDF from the HTML file
            pdf_output_path = 'sales_category_report.pdf'
            pdfkit.from_file('temp_report.html', pdf_output_path, configuration=config)

            # Send the generated PDF file as a response
            response = make_response(open(pdf_output_path, 'rb').read())
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = 'inline; filename=sales_category_report.pdf'
            os.remove('temp_report.html')
            os.remove(pdf_output_path)
            return response
       # Check if referrer exists and is not the same as the current URL to prevent redirection loop
    referrer = request.referrer    
    if referrer and referrer != request.url:
        redirect(referrer)


@web.route('/ch_pwd', methods=['GET', 'POST'])
def change_pwd():
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
            return  render_template('admin/ch_pwd.html')
        else:
            flash('Incorrect current password.', 'error')
            return redirect(url_for('change_pwd'))

    return render_template('admin/ch_pwd.html')