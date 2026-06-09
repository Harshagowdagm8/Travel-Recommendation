import mysql.connector

link = mysql.connector.connect(
    host = 'localhost', 
    user = 'root', 
    password = '', 
    database = 'travelrecommendation_2024'
)

def predictresult(request):
    result = []   
    cursor = link.cursor() 
    city = request.form["city"] 
    rating = request.form["rating"] 
    distance = request.form["distance"]  
    
    query = "SELECT * FROM travelrecommendation_2024_predict where city = '"+city+"' and rating >= '"+rating+"' ORDER BY distance asc limit 20" 
    print(query)
    cursor.execute(query) 
    result = cursor.fetchall()
    return result
      
    

    