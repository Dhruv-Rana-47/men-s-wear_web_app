from shop.app import web

if __name__=="__main__":
    web.run(debug=True)
    
# run xampp server before running
#  .\myvenv\Scripts\activate   
# # python run.py
    
    # migration command
# $env:FLASK_APP = "run.py" 
# python -m flask run
#  flask db upgrade
# flask db migrate -m "order and order_detail change and old deleted "