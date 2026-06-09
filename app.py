from flask import Flask, flash, redirect, render_template, request, session, url_for
import mysql.connector, random, string, os, csv 
from predict import predictresult



app = Flask(__name__)
app.secret_key = "Qazwsx@123"  



link = mysql.connector.connect(
    host = 'localhost', 
    user = 'root', 
    password = '', 
    database = 'travelrecommendation_2024'
)




@app.after_request
def add_header(response):
  
  response.cache_control.no_store = True
  return response



 




@app.route('/')
def index():
  
  return render_template('index.html')    


 






@app.route('/login', methods=['GET', 'POST'])
def login(): 
    
  if 'user' in session:
    return redirect(url_for('predict'))

  if request.method == "GET":
    return render_template('login.html') 
    
  else:
    cursor = link.cursor()
    try: 
      email = request.form["email"]
      password = request.form["password"]
      cursor.execute("SELECT * FROM travelrecommendation_2024_user WHERE email = '"+email+"' AND password = '"+password+"'")
      user = cursor.fetchone()
      if user:
        session['user'] = user[3]
        session['username'] = user[2] 
        return redirect(url_for('predict'))
      else:
        return render_template('login.html', error='Invalid email or password') 
    
    except Exception as e:
      error = e
      return render_template('login.html', error=error)
      
    finally:
        cursor.close() 






 



@app.route('/register', methods=['GET', 'POST'])
def register():
      
  if 'user' in session:
    return redirect(url_for('predict'))

  if request.method == "GET": 
    return render_template('register.html') 
  
  else: 
    cursor = link.cursor()  
    try: 
      name = request.form["name"]
      email = request.form["email"]
      password = request.form["password"] 
      phone = request.form["phone"] 
      uid = 'uid_'+''.join(random.choices(string.ascii_letters + string.digits, k=10))
      cursor.execute("SELECT * FROM travelrecommendation_2024_user WHERE email = %s", (email,))
      user = cursor.fetchone()
 
      if user:
        return render_template('register.html', exists='Email already exists') 
      else:
        cursor.execute("INSERT INTO travelrecommendation_2024_user (uid, name, email, password, phone) VALUES ('"+uid+"', '"+name+"', '"+email+"', '"+password+"', '"+phone+"')")
        link.commit()
        return render_template('register.html', success='Registration successful') 
       
    except Exception as e:
      error = e
      return render_template('register.html', error=error)
      
    finally:
        cursor.close()     


 








@app.route('/forecast', methods=['GET', 'POST'])
def forecast(): 
    
  if 'user' not in session:
    return redirect(url_for('login'))
  
  cursor = link.cursor()
  try: 
    cursor.execute("SELECT * FROM travelrecommendation_2024_predict limit 500")
    data = cursor.fetchall()
    cursor.execute("SHOW COLUMNS FROM travelrecommendation_2024_predict")
    columns = [column[0] for column in cursor.fetchall()] 
    link.commit()
    return render_template('forecast.html',data = data,columns = columns) 
    
  except Exception as e:
    error = e
    return render_template('error.html', error=error)
      
  finally:
    cursor.close()  










@app.route('/upload', methods=['GET', 'POST'])
def upload():

  if 'user' not in session:
    return redirect(url_for('login'))
  
  if request.method == "GET": 
    return render_template('upload.html') 

  else:
    cursor = link.cursor()
    try: 
      file = request.files["file"] 
      filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)) + '\\static\\docs', file.filename)
      file.save(filepath) 
      rows = []
        
      with open(filepath, 'r', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)  
        for row in csvreader:
          rows.append(row) 

      for row in rows[1:]: 
        if row and row[0] and row[0][0] != "":
          query=""
          query=f"insert into travelrecommendation_2024_predict (`uid`,`city`,`place`,`rating`,`distance`,`description`) values ('uid_"+"".join(random.choices(string.ascii_letters + string.digits, k=10))+"',"

          for col in row: 
            col = col.replace("'", "''")
            query =query+"'"+col+"',"

          query =query[:-1]
          query=query+");"
          print(query)
          cursor.execute(query)
          link.commit()

      return render_template('upload.html', success='Upload successful', file=file.filename) 
    
    except Exception as e:
      error = e
      return render_template('error.html', error=error)
      
    finally:
        cursor.close() 










@app.route('/predict', methods=['GET', 'POST'])
def predict():

  if 'user' not in session:
    return redirect(url_for('login'))
  
  if request.method == "GET": 
    cursor = link.cursor()
    try:  
      query = "SELECT city FROM travelrecommendation_2024_predict group by city order by city asc;"
      cursor.execute(query)
      city = cursor.fetchall()  
      return render_template('predict.html', city=city)

    except Exception as e:
      error = e
      return render_template('error.html', error=error)  
      
    finally:
        cursor.close() 
    

  else:
    cursor = link.cursor()

    try:  
      city = request.form["city"] 
      rating = request.form["rating"] 
      distance = request.form["distance"]  

      result = predictresult(request) 

      uid = 'uid_'+''.join(random.choices(string.ascii_letters + string.digits, k=10))
      query = f"INSERT INTO travelrecommendation_2024_history (uid, user, username, city, rating, distance) VALUES ('"+uid+"', '"+session['user']+"', '"+session['username']+"', '"+city+"', '"+rating+"', '"+distance+"')"
      print(query)
      cursor.execute(query) 
      link.commit() 
      return render_template('result.html', result=result) 
    
    except Exception as e:
      error = e
      return render_template('error.html', error=error)
      
    finally:
        cursor.close() 








@app.route('/cleardataset', methods = ['POST'])
def cleardataset():

  if 'user' not in session:
    return redirect(url_for('login'))
  
  cursor = link.cursor()
  try: 
    query="delete from travelrecommendation_2024_predict"
    cursor.execute(query) 
    link.commit()
    flash('Data cleared successfully', 'success')
    return redirect(url_for('upload'))
  
  except Exception as e:
    error = e
    return render_template('error.html', error=error)
    
  finally:
      cursor.close() 






@app.route('/logout')
def logout():
    
    session.pop('user', None)
    session.pop('username', None)
    return redirect(url_for('index'))







if __name__ == '__main__':
    app.run(debug=True)
