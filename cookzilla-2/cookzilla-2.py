#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 24 17:04:56 2022

@author: aaqil
"""

#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect, flash
import pymysql.cursors

#for uploading photo:
from app import app
#from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename

#for encrypting user passwords
from passlib.hash import sha256_crypt

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])



#configure MySQL

conn = pymysql.connect(host='localhost', port=8889, user='root',password='root',db= 'CookZillaTableDefinition',charset='utf8', cursorclass=pymysql.cursors.DictCursor)



def allowed_image(filename):

    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False


def allowed_image_filesize(filesize):

    if int(filesize) <= app.config["MAX_IMAGE_FILESIZE"]:
        return True
    else:
        return False



#Define a route to the hello function

@app.route('/', methods = ['GET', 'POST'])
def hello():
    
    if request.method=='POST':
        #searchid=request.form['id']
        if request.form['action']=='Submit':
            recipeID = int(request.form['Uid'])
            cursor = conn.cursor();
            #NATURAL JOIN Review
            query='SELECT * FROM Recipe NATURAL JOIN RecipeTag  WHERE Recipe.recipeID = %s'
            cursor.execute(query, (recipeID))
            step=cursor.fetchall()
            
            
            #query2 = 'SELECT * FROM Step WHERE recipeID = (%s)'
            #cursor.execute(query2, (recipeID))
            #step =cursor.fetchall()
            
           # conn.commit()
           
            cursor.close()
            #posts=data,
            
            return render_template('search_result.html',  step=step)
           # return render_template('search_result.html', posts=data)
            
            return render_template('search_result.html')
        elif request.form['action'] =='Search by Tag':
            tag = request.form['tags'];
            cursor=conn.cursor();
            #NATURAL JOIN Review
            querystars = 'CREATE OR REPLACE VIEW avgStars AS (SELECT recipeID, avg(stars) as Avg FROM Review GROUP BY recipeID)'
            cursor.execute(querystars)
            
            query3='SELECT * from avgstars WHERE recipeID = %s'
          #  cursor.execute(query3, ())
            
            
            query='SELECT * from Recipe Natural JOIN RecipeTag  WHERE RecipeTag.tagText=(%s)'
            cursor.execute(query, (tag))
            tagdata = cursor.fetchall()
            
            
          #  query2 = 'SELECT * FROM Step WHERE recipeID in (SELECT recipeID FROM RecipeTag WHERE tagText=(%s))'
           # cursor.execute(query2, (tag))
           # tagstep =cursor.fetchall()
            
           # conn.commit()
           
            cursor.close()
            
            return render_template('search_result.html',step=tagdata)
        elif request.form['action'] == 'Search by Rating':
            rating = request.form['rating'];
            cursor=conn.cursor();
            query = 'CREATE OR REPLACE VIEW avgStars AS (SELECT recipeID, avg(stars) as Avg FROM Review GROUP BY recipeID)'
            cursor.execute(query)
            
            
            
         #   starquery='SELECT * FROM avgStars WHERE avg >=%s'
          #  cursor.execute(starquery, rating)
          #  stardata=cursor.fetchall()
            
            
            query2='SELECT * FROM Recipe NATURAL JOIN avgStars NATURAL JOIN RecipeTag WHERE recipeID in (SELECT recipeID from avgStars WHERE Avg >=%s)'
            
          #  query = 'SELECT * FROM Recipe where recipeID in (SELECT recipeID, avg(stars) as AvgStars FROM Review WHERE stars > (%s) GROUP BY recipeID ORDER BY AvgStars DESC) '
            
            cursor.execute(query2, (rating))
            ratingdata=cursor.fetchall()
            
            return render_template('search_result.html',step=ratingdata)
        
        elif request.form['action']=='Search by Rating and Tag':
            rating = request.form['rating'];
            tags = request.form['tags'];
            cursor=conn.cursor();
            
            query = 'CREATE OR REPLACE VIEW avgStars AS (SELECT recipeID, avg(stars) as Avg FROM Review GROUP BY recipeID)'
            cursor.execute(query)
            
       #     starquery='SELECT * FROM avgStars WHERE recipeID=%s'
        #    cursor.execute(starquery)
         #   stardata=cursor.fetchall()
            
            query2='SELECT  * FROM Recipe NATURAL JOIN avgStars NATURAL JOIN RecipeTag WHERE recipeID in (SELECT recipeID from avgStars WHERE Avg =%s) AND tagText=%s'
            
          #  query = 'SELECT * FROM Recipe where recipeID in (SELECT recipeID, avg(stars) as AvgStars FROM Review WHERE stars > (%s) GROUP BY recipeID ORDER BY AvgStars DESC) '
            
            cursor.execute(query2, (rating, tags))
            querydata=cursor.fetchall()
            return render_template('search_result.html',step=querydata)
            
            
            
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/search')
def search():
    return render_template('search_result.html')

@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
    #grabs information from the forms (user entries)
    username=request.form['username']
    password=request.form['password']
    fName = request.form['fName']
    lName = request.form['lName']
    email = request.form['email']
    profile = request.form['profile']
    
        #add salt to pw
    #cursor to send queries
    cursor = conn.cursor();
   
    #execute query
    query = 'SELECT * FROM person WHERE userName =%s'
    cursor.execute(query, (username))
    
    data=cursor.fetchone()
    error = None

    if(data):
        error="This user already exists"
        return render_template('login.html', error=error)
    else:
        ins='INSERT INTO Person Values(%s,%s,%s,%s,%s,%s)'
        
        
        #adding salt to password
        
        salt = "c00km3"
        password = password + salt
        
        #generating hash for password
        password=sha256_crypt.hash(password)
        
        
        cursor.execute(ins, (username, password, fName, lName, email, profile))
        conn.commit()
        cursor.close()
        return render_template('index.html')
    
    
    
@app.route('/loginAuth', methods=['GET','POST'])
def loginAuth():
    #grab info from forms (user entries)
    username= request.form['username']
    password=request.form['password']
    
    #cursor to send queries
    
    cursor2 = conn.cursor()
    
 #   correct_pass= sha256_crypt.verify(password,passTable)
    
    #execute query
   # query= 'SELECT * FROM Person WHERE userName = %s and password = %s'
    
    query2= 'SELECT * FROM Person WHERE userName = %s'
    
    
    #encrypting the password and sending it into the table
    salt = "c00km3"
    password = password + salt
    
    password= sha256_crypt.hash(password)
    
   # cursor.execute(query, (username, password))
    
    cursor2.execute(query2, (username))
    if(cursor2.rowcount==0):
        error = 'Invalid username or password'
        return render_template('login.html', error=error)
    
 
    data2=cursor2.fetchone()['password']
    #data2=cursor2.fetchone()['password']
    
   
    
    
    pas=data2
    
     
     
    
    cursor2.close()
    
    passw= request.form['password']
    passw = passw+salt
    
    if(sha256_crypt.verify(passw, pas)):
        session['username'] = username
        flash("You are now logged in")
        return redirect(url_for('home'))
      
    else:
        error = 'Invalid username or password'
        return render_template('login.html', error=error)


@app.route('/home')
def home():
    
    if session.get('username'):
        user=session['username']
        cursor=conn.cursor();
        query= 'SELECT * FROM RECIPE WHERE postedBy in (SELECT userName FROM Person WHERE userName = %s)'
        cursor.execute(query, (user))
        data = cursor.fetchall()
        cursor.close()
        return render_template('home.html', username=user, recipes=data)
    else:
        return redirect('/')


#@app.route('/'):
 #   def uploadRecipe():
  #      return render_template('postRecipe.html')

@app.route('/postRecipe')
def postRecipe():
   if not session.get("username"):
       return redirect('/')
   
   return render_template('postRecipe.html')
    

@app.route('/post_Recipe', methods=['GET','POST'])
def post_Recipe():

   
    username=session['username']
   # recipe_id = request.form['recipeID']
    title = request.form['title']
    num_Serv = request.form['numServings']
    tags = request.form['tags']
    url = request.form['picture_URL']
       
    postedBy = username
    
    
    stepDesc = request.form.getlist('stepDesc')
    
    cursor = conn.cursor();
    query= 'INSERT into Recipe (title, numServings, postedBy )VALUES (%s,%s,%s)'
   # query2='INSERT into RecipeTag VALUES (%s,%s)'
    queryrep='SELECT LAST_INSERT_ID()'
    
    query2='INSERT into RecipeTag VALUES (LAST_INSERT_ID(),%s)'
    #query3='INSERT into Step VALUES (%s,%s,%s)'
    
    query3='INSERT into Step VALUES (%s,LAST_INSERT_ID(),%s)'
    
    query4='INSERT into RecipePicture VALUES(LAST_INSERT_ID(), %s)'
    
    # recipeID, iName, unitName, amount
   # query4='INSERT into RecipeIngredient VALUES (%s, %s, %s, %s)'
    
    
   # query_ins_ing = "INSERT INTO Ingredient VALUES (%s,%s) SELECT * FROM Ingredient WHERE NOT EXISTS(SELECT * FROM Ingredient EXCEPT(SELECT iName FROM Ingredient WHERE iName = %s))"
   # query_ins_ing = "INSERT IGNORE INTO Ingredient VALUES (%s,%s) "
    cursor.execute(query,( title, num_Serv, postedBy))
    
    cursor.execute(queryrep)
    
    data = cursor.fetchone()
    
    #query to get recipe ID
   # queryrepID = 'SELECT recipeID from Recipe '
    #cursor.execute()
    cursor.execute(query2, ( tags))
    #cursor.execute(query2, (recipe_id, tags))
    i=1
    for value in stepDesc:
        #cursor.execute(query3, (i, recipe_id ,[value]))
        cursor.execute(query3, (i ,[value]))
        i+=1
    
    cursor.execute(query4, (url))
    
    
  #  for value1 in ingredients:
     #   cursor.execute(query_ins_ing, ([value1], "placeholder"))
        
     #   cursor.execute(query4, (recipe_id, [value1], unit, amount))
        
    conn.commit()
    cursor.close()
    return render_template('ingredients_table.html', rid=data)
    
#@app.route('/')
#def searchresult():
#    return render_template('search_result.html')

@app.route('/ingredients_table', methods=['GET', 'POST'])
def ingr_table():
    
    #repid = request.form.get('repid')
    ingredient=request.form.getlist('ingredients')
    unit = request.form.getlist('unit')
    amount = request.form.getlist('amount')
    cursor=conn.cursor();
    query_ins_ing = "INSERT IGNORE INTO Ingredient VALUES (%s,%s) "
   # query4='INSERT into RecipeIngredient VALUES (%s, %s, %s, %s)'
    
    query4='INSERT into RecipeIngredient VALUES (LAST_INSERT_ID(), %s, %s, %s)'
    
    
    for value in ingredient:
        cursor.execute(query_ins_ing, ([value], "placeholder"))
        conn.commit()
      
    cursor.close()

    cursor=conn.cursor();    
    for (a,b,c) in zip(ingredient, unit, amount):
        cursor.execute(query4, (a, b, c))
        
        
    conn.commit()
    cursor.close()
        
    return redirect('/home')

@app.route('/groups', methods = ['GET', 'POST'])
def groups():
    
    query = 'SELECT * FROM `Group`'
    
    cursor=conn.cursor();
    cursor.execute(query)
    
    result = cursor.fetchall()
    
    
    return render_template('groupjoin.html', data=result)
    

@app.route('/results', methods=['GET','POST'])
def searchR():
    if request.method=='POST':
        
        #searchid=request.form['id']
        if request.form['action']=='Submit':
            recipeID = int(request.form['Uid'])
            cursor = conn.cursor();
            #NATURAL JOIN Review
            query='SELECT * FROM Recipe NATURAL JOIN RecipeTag  WHERE Recipe.recipeID = (%s)'
            cursor.execute(query, (recipeID))
            step=cursor.fetchall()
            
            
            #query2 = 'SELECT * FROM Step WHERE recipeID = (%s)'
            #cursor.execute(query2, (recipeID))
            #step =cursor.fetchall()
            
           # conn.commit()
           
           #try creating a view before everything and referencing that for parameters
           
            cursor.close()
           # posts=data,
            return render_template('search_result.html',  step=step)
           # return render_template('search_result.html', posts=data)
            
            return render_template('search_result.html')
        elif request.form['action'] =='Search by Tag':
            tag = request.form['tags'];
            cursor=conn.cursor();
            #NATURAL JOIN Review
            
            query='SELECT * from Recipe Natural JOIN RecipeTag  WHERE RecipeTag.tagText=(%s)'
            cursor.execute(query, (tag))
            tagdata = cursor.fetchall()
            
            
          #  query2 = 'SELECT * FROM Step WHERE recipeID in (SELECT recipeID FROM RecipeTag WHERE tagText=(%s))'
           # cursor.execute(query2, (tag))
           # tagstep =cursor.fetchall()
            
           # conn.commit()
           
            cursor.close()
            
            return render_template('search_result.html',step=tagdata)
        elif request.form['action'] == 'Search by Rating':
            rating = request.form['rating'];
            cursor=conn.cursor();
            query = 'CREATE OR REPLACE VIEW avgStars AS (SELECT recipeID, avg(stars) as Avg FROM Review GROUP BY recipeID)'
            cursor.execute(query)
            query2='SELECT * FROM Recipe NATURAL JOIN RecipeTag NATURAL JOIN avgStars WHERE recipeID in (SELECT recipeID from avgStars WHERE Avg =%s)'
            
          #  query = 'SELECT * FROM Recipe where recipeID in (SELECT recipeID, avg(stars) as AvgStars FROM Review WHERE stars > (%s) GROUP BY recipeID ORDER BY AvgStars DESC) '
            
            cursor.execute(query2, (rating))
            ratingdata=cursor.fetchall()
            
            return render_template('search_result.html',step=ratingdata)
        
        elif request.form['action']=='Search by Rating and Tag':
            rating = request.form['rating'];
            tags = request.form['tags'];
            cursor=conn.cursor();
            
            query = 'CREATE OR REPLACE VIEW avgStars AS (SELECT recipeID, avg(stars) as Avg FROM Review GROUP BY recipeID)'
            cursor.execute(query)
            
            
            query2='SELECT * FROM Recipe NATURAL JOIN RecipeTag NATURAL JOIN avgStars WHERE Recipe.recipeID in (SELECT recipeID from avgStars WHERE Avg =%s) AND tagText=%s'
            
          #  query = 'SELECT * FROM Recipe where recipeID in (SELECT recipeID, avg(stars) as AvgStars FROM Review WHERE stars > (%s) GROUP BY recipeID ORDER BY AvgStars DESC) '
            
            cursor.execute(query2, (rating, tags))
            querydata=cursor.fetchall()
          
            
          # posts = zip(querydata, ratingNo)
            
            return render_template('search_result.html',step=querydata)
    
    
    return render_template('results.html')
    
    
@app.route('/search_result', methods=['GET', 'POST'])
def search_result():
    
   #  recipeID = request.form['id']
   #  cursor = conn.cursor();
   #  query='SELECT * FROM Recipe WHERE recipeID = (%d)'
   #  cursor.execute(query, (recipeID))
   # # conn.commit()
   #  data=cursor.fetchall()
    
   #  query2 ='SELECT * FROM Step WHERE recipeID = (%d)'
   #  cursor.execute(query2, (recipeID))
   #  step = cursor.fetchall()
    
   #  cursor.close()
    
    recipeID = request.form['id']
    cursor = conn.cursor();
    query='SELECT * FROM Recipe WHERE recipeID = (%d)'
    cursor.execute(query, (recipeID))
   # conn.commit()
    step=cursor.fetchall()
    
    #query2 ='SELECT * FROM Step WHERE recipeID = (%d)'
    #cursor.execute(query2, (recipeID))
    #data = cursor.fetchall()
    
    #posts=data
    cursor.close()
    return render_template('search_result.html', step=step)
   # return render_template('search_result.html', posts=data)
    

@app.route('/fullRecipe', methods=['GET','POST'])
def fullRecipe():
     #if request.method=='POST':
         repID = request.form.get('repid')
         cursor = conn.cursor();
         #NATURAL JOIN Review 
         query='SELECT * FROM Recipe NATURAL JOIN RecipeTag WHERE Recipe.recipeID = (%s)'
    
         
         #cursor.execute(query, ('repID'))
         #data=cursor.fetchall()
         #query='SELECT * FROM Recipe WHERE recipeID = (%s)'
         cursor.execute(query, (repID))
         conn.commit()
         data=cursor.fetchall()
         
          
         queryview = 'CREATE OR REPLACE VIEW avgStars AS (SELECT recipeID, avg(stars) as Avg FROM Review GROUP BY recipeID)'
         cursor.execute(queryview)
         
         ratingquery='SELECT Avg from avgstars WHERE recipeID = %s'
         
         cursor.execute(ratingquery,(repID))
         
         stars = cursor.fetchall()
         
         
         
         query2 ='SELECT * FROM Step WHERE recipeID = (%s)'
         cursor.execute(query2, (repID))
         step = cursor.fetchall()
       
         
         query3 = 'SELECT * FROM Review WHERE recipeID = %s'
         cursor.execute(query3, (repID))
         reviews = cursor.fetchall()
         
         
         query4 = 'SELECT * from RecipeIngredient WHERE recipeID = %s'
         cursor.execute(query4, (repID))
         ingredients = cursor.fetchall()
         
         query5 = 'SELECT * from RecipePicture WHERE recipeID=%s'
         cursor.execute(query5, (repID))
         pictures = cursor.fetchall()
         
         query6 = 'SELECT * from ReviewPicture WHERE recipeID = %s'
         cursor.execute(query6, (repID))
         reviewPictures = cursor.fetchall()
         
         
         cursor.close()
         
         
         return render_template('fullResult.html', reviewPictures = reviewPictures, stars=stars, pictures=pictures, repID = repID, posts=data, step=step, reviews=reviews, ingredients=ingredients)
     
    
     #return render_template('fullResult.html')
     
@app.route('/postReview', methods=['GET','POST'])
def postReview():  
    if not session.get("username"):
        return redirect('/')
    repID = request.form["repid"]
    return render_template('postReview.html', repID = repID)
    
@app.route('/post_Review', methods=['GET','POST'])
def post_Review():
    

    
    if session.get("username"):
        user = session.get("username")
        cursor=conn.cursor()
       # repID = repID
        repID = request.form['repid']
        title = request.form['title']
        desc = request.form['desc']
        stars = request.form['stars']
        url = request.form['picture_URL']
        
        
     
        query = 'INSERT INTO Review VALUES(%s,%s,%s,%s,%s)'
        cursor.execute(query,(user, repID, title, desc, stars))
       
        
        query2 = 'INSERT INTO ReviewPicture VALUES (%s, %s, %s)'
        cursor.execute(query2, (user, repID, url))
        conn.commit()
        cursor.close()
        
        
        return redirect('results')
    else:
        return redirect('/')
        
    
    
    
    #return render_template('postReview.html')
    
@app.route('/viewGroups', methods=['GET','POST'])
def groupresult():
    user = session.get("username")
    cursor=conn.cursor()
    query = 'Select * FROM GroupMembership WHERE memberName=%s'
    
    cursor.execute(query,(user))
    
    data = cursor.fetchall()
        
    cursor.close()
    return render_template('groupresult.html', groups=data)


@app.route('/postEvent', methods =['GET','POST'])
def pEvent():
    
    gName = request.form['gName']
    gCreator=request.form['gCreator']
    return render_template('postEvent.html', gName=gName, gCreator=gCreator)

@app.route('/post_Event', methods=['GET','POST'])
def postEvent():
    
    gName= request.form['gName']
    gCreator = request.form['gCreator']
    user = session.get('username')
    eName = request.form['eName']
    eDesc = request.form['eDesc']
    eDate = request.form['eDate']

    url = request.form['picture_URL']
    
    cursor=conn.cursor()
   
   #use a query to get the gName and group creator, and pass that in
   #this way, anyone in the group can post an event to that group
   #maybe add pictures to that as well
   
   #query= "SELECT gName, gCreator from `Group` WHERE "
   
    query= "INSERT into `EVENT` (eName, eDesc, eDate, gName, gCreator) VALUES(%s, %s, %s, %s, %s)"
    
    cursor.execute(query, (eName, eDesc, eDate, gName, gCreator))
    conn.commit()
    
  
    
    query2 = "INSERT into EventPicture VALUES (LAST_INSERT_ID(),%s)"
    cursor.execute(query2,( url))
    conn.commit()
    
    cursor.close()
    
    return redirect('/viewGroups')
    

@app.route('/joinGroup', methods=['GET','POST'])
def joinGroup():
    cursor = conn.cursor()
    user = session.get('username')
    gName = request.form['gName']
    gCreator = request.form['gCreator']
    
    
    
    query = "INSERT into GroupMembership VALUES(%s,%s,%s)"
    
    cursor.execute(query,(user, gName, gCreator))
    conn.commit()
    cursor.close()
    
    #return render_template('/home.html')
    return redirect('/viewGroups')


    
@app.route('/viewGroupDetails', methods=['GET','POST'])
def groupDetails():
    
    
    
    user = session.get("username")
    gName = request.form['gName']
    gCreator = request.form['gCreator']

    
    cursor=conn.cursor()
    query = 'SELECT * FROM `Group`  WHERE gName = (%s) and gCreator = (%s)'
    
    cursor.execute(query,(gName, gCreator))
    data = cursor.fetchall()
    
    
    query2 = 'SELECT * FROM Event WHERE gName = (%s) and gCreator = (%s)'
    cursor.execute(query2, (gName,gCreator))
    eventData = cursor.fetchall()
    
   
    
    
    
    return render_template('fullGroupResult.html', group=data, events=eventData)
    


@app.route('/viewGroupPics', methods=['GET', 'POST'])
def groupPics():
    eID = request.form['eID']
    query = 'SELECT * FROM EventPicture WHERE eID = %s'
    
    cursor=conn.cursor()
    
    cursor.execute(query, eID)
    
    eventPics = cursor.fetchall()
    
    return render_template('groupPictures.html', eventPics=eventPics)

                       
                       
                       
                       

@app.route('/logout')
def logout():
    
    if session.get("username"):
        session.pop('username')
    return redirect('/')

app.secret_key='keythatyouwontknowwwwww@@@@@@'

if __name__ =="__main__":
    app.run('127.0.0.1', 5000, debug=True)