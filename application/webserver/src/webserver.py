from flask import Flask, jsonify, request, json
from flask_mysqldb import MySQL
from datetime import datetime
from flask_cors import CORS, cross_origin
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_jwt_extended import (create_access_token)
import googlemaps

app = Flask(__name__)

app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'polarity'
#app.config['MYSQL_DB'] = 'Presso'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['JWT_SECRET_KEY'] = 'secret'
app.config['MYSQL_HOST'] = 'mysql'
#app.config['MYSQL_PASSWORD'] = 'priyanka'
#app.config['MYSQL_HOST'] = 'localhost'

mysql = MySQL(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
CORS(app)

@app.route('/tweets', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def register():
    gmaps = googlemaps.Client(key='AIzaSyCT61OrlkTc9V1LGjNXBfHPt7F81K5iSA0')
    coordinates={'latitude':[],'longitude':[]}
    cur = mysql.connection.cursor()
    sql_query = "SELECT * FROM POLARITY_TBL"
    cur.execute(sql_query)
    records = cur.fetchall()

    lat = 0
    long = 0
    '''
    for i in range(len(records)):
        print(records[i][2].strip())
        try:
            print(gmaps.geocode(records[i][2].strip()))
            location=gmaps.geocode(records[i][2].strip())
            for j in location:
                coordinates['latitude'].append(j['geometry']['location']['lat'])
                coordinates['longitude'].append(j['geometry']['location']['lng'])
        except:
            coordinates['latitude'].append(0)
            coordinates['longitude'].append(0)
            pass
     '''
        
    return jsonify({"result":records})




if __name__ == '__main__':
    app.run(port=8080, host='0.0.0.0', debug='true',ssl_context='adhoc')
    #app.run(port=8080, host='localhost', debug='true')
