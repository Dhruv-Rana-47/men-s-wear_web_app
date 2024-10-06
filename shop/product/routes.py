from flask import *
from shop.app import web,db
from .models import Category,Subcategory,Product,Color,Size,Gallery
from flask_login import login_required,current_user
from sqlalchemy import func
from werkzeug.utils import secure_filename
import os


# Define allowed extensions for image files
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Function to check if a filename has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@web.route('/product',methods=['Get','post'])
@login_required
def pro():
    if current_user.id == 1 and current_user.is_authenticated:
        
        products = Product.query.all()  # Fetch all category items from the database
        return render_template("admin/product/pro_panel.html", products=products)



@web.route('/addpro',methods=['Get','post'])
@login_required
def add_pro():
    if current_user.id == 1 and current_user.is_authenticated:
    
     
        if request.method=='POST':
            existing_pro= Product.query.all()
            if existing_pro:
                new_id = max(product.pid for product in existing_pro) + 1
            # If there are records, fetch the maximum ID and increment it by 1
            else:
                new_id = 1001

            # If there are no records, set the new ID as 1
            pname=request.form.get("pname")
            price=request.form.get("price")
            desc=request.form.get("desc")
            mat=request.form.get("material")
        
            cid=request.form.get("cid")
            sub_id=request.form.get("sub_id")
            size_id=request.form.get("size")
            col_id=request.form.get("color")
            stock=request.form.get("stock")
            # fatching AND uploading image 

            img1 = request.files['img1']
            img2 = request.files['img2']
            if img1 and img2 and allowed_file(img1.filename) and allowed_file(img2.filename):
                img1.save(os.path.join(web.config['UPLOAD_FOLDER'],img1.filename))
                img2.save(os.path.join(web.config['UPLOAD_FOLDER'],img2.filename))
                
            else:
                return "Please select valid image files"

        #fatch details of sleeves and neck and store it into variable if empty store none
                        
            if not request.form.get("sleeves") and not request.form.get("neck"):
                sleeves = None
                neck = None
            else:
                sleeves = request.form.get("sleeves")
                neck = request.form.get("neck")
            
            new_product = Product(
                            pid=new_id,
                            pname=pname,
                            price=price,
                            description=desc,
                            material=mat,
                            sleeves=sleeves,
                            neck=neck,
                            cid=cid,
                            sub_id=sub_id,
                            sid=size_id,
                            color_id=col_id,
                            stock=stock,
                            image1=os.path.join(web.config['UPLOAD_FOLDER'],img1.filename),
                            image2=os.path.join(web.config['UPLOAD_FOLDER'],img2.filename)
                        )
            gallery=Gallery(path1=os.path.join(web.config['UPLOAD_FOLDER'],img1.filename),
                            path2=os.path.join(web.config['UPLOAD_FOLDER'],img2.filename),
                            pid=new_id)
            try:
                db.session.add(new_product)
                db.session.add(gallery)
                db.session.commit()
                pro=Product.query.filter_by(pid=new_id).first()
                flash(f' {pro.pname}  is successfully added to the database',"success")
                return redirect("/product")
                
        
            except Exception as e:
                db.session.rollback()  # Rollback transaction if an error occurs
                flash(str(e), 'error')  # Flash the error message with 'error' category
                return redirect("/product")
            
            
        else:
            color=Color.query.all()
            size=Size.query.all()
            category=Category.query.all()
            subcategory=Subcategory.query.all()
            return render_template("admin/product/addpro.html",colors=color,sizes=size,cat=category,subcat=subcategory)



@web.route('/delete_pro/<int:pro_id>', methods=['GET', 'POST'])
@login_required
def delete_pro(pro_id):
    if current_user.id == 1 and current_user.is_authenticated:
    
        product = Product.query.get(pro_id)
        if product:
            try:
                db.session.delete(product)
                db.session.commit()
                flash(f'product"{product.pname}" deleted successfully', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Failed to delete product "{product.pname}"', 'danger')
        else:
            flash('product not found', 'danger')

        return redirect('/product')

@web.route('/delete_selected_pro', methods=['GET','POST'])
@login_required
def delete_selected_pro():
    if current_user.id == 1 and current_user.is_authenticated:
    
        if request.method == 'POST':
            if 'delete_selected' in request.form:
                selected_category_ids = request.form.getlist('selected_product[]')
                
                for pro_id in selected_category_ids:
                    products = Product.query.get(pro_id)
                    if products:
                        db.session.delete(products)

                db.session.commit()
                flash('Selected products deleted successfully', 'success')
                return redirect('/product') 
        

     # Redirect to the category page after deletion or addition

@web.route('/edit_pro/<int:pro_id>', methods=['GET', 'POST'])
@login_required
def edit_pro(pro_id):
    if current_user.id == 1 and current_user.is_authenticated:
    
        prod = Product.query.get(pro_id)
        if not prod:
            # Handle case where category with the provided ID does not exist
            return "product not found", 404
        
        if request.method == 'POST':
            # Update category data based on form submission
            prod.pname = request.form['pname']
            # Add additional fields as needed
            
            # Commit changes to the database
            db.session.commit()
            flash('product updated successfully', 'success')
            # Redirect to category list page after successful edit
            return redirect('/product')
        else:
            # Render the edit form with pre-filled data
            return render_template('admin/product/editpro.html', prod=prod)
    
# category routes ended<-<-<-----<
    
# sub category routes->->->>->>


