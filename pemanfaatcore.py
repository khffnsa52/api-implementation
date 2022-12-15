from flask import *
import jwt
import datetime
from functools import wraps

app = Flask(__name__)

app.config['SECRET_KEY'] = 'iniAdalahSecretKey'

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')

        if not token:
            return jsonify({'message' : 'Token is missing!'}), 403
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'message' : 'Token is invalid!'}), 403
        
        return f(*args, **kwargs)
    return decorated


@app.route('/')
def login():
    auth = request.authorization

    if auth and auth.username == 'khafifa' and auth.password == 'nisa':
        # generate token
        token = jwt.encode({'user' : auth.username, 
                            'exp' : datetime.datetime.utcnow() + 
                            datetime.timedelta(seconds=30)}, 
                            app.config['SECRET_KEY'])

        return jsonify({'token' : token.decode('UTF-8')})
    return make_response('Could not verify!', 401, {'WWW-Authenticate' : 'Basic realm="Login Required"'})

@app.route('/protected', methods=['GET', 'POST'])
@token_required
def protected():
    if request.method == 'GET':
        session.permanent = True
        token = request.args.get('token')
        session["main"] = token
        return redirect(url_for("main"))
    else:
        if "main" in session:
            return redirect(url_for("login"))


@app.route('/main', methods=['GET', 'POST'])
def main():
    if "main" in session:
        if request.method == 'POST':
            age = int(request.form['age'])
            sex = request.form['sex']
            chest_pain_type = request.form['chest_pain_type']
            cholesterol = int(request.form['cholesterol'])
            max_hr = int(request.form['max_hr'])

            #informasi tambahan tentang stroke
            jumlah_sakit_jantung = 47
            jumlah_stroke = 250
            stroke = (jumlah_sakit_jantung/jumlah_stroke)

            #categorization
            #usia
            if age < 40:
                age_category = 'Young'
                age_rate = 0.35
            elif age < 60:
                age_category = 'Middle'
                age_rate = 0.55
            else:
                age_category = 'Old'
                age_rate = 0.83
    
            #gender
            if sex == 'F':
                gender = "Female"
                gender_rate = 0.14
            elif sex == 'M':
                gender = 'Male'
                gender_rate = 0.79
            
            #chest pain type
            if chest_pain_type == 'TA':
                pain_type = 'Typical Angina'
                pain_type_rate = 0.56
            elif chest_pain_type == 'ATA':
                pain_type = 'Atypical Angina'
                pain_type_rate = 0.11
            elif chest_pain_type == 'NAP':
                pain_type = 'Non-Anginal Pain'
                pain_type_rate = 0.43
            else:
                pain_type = 'Asymptomatic'
                pain_type_rate = 0.81
    
            #cholesterol
            if cholesterol < 200:
                cholesterol_risk = 'Low'
                chol_rate = 0.71
            elif cholesterol < 400:
                cholesterol_risk = 'Middle'
                chol_rate = 0.43
            else:
                cholesterol_risk = 'High'
                chol_rate = 0.67
    
            #max_hr
            if max_hr < 100:
                max_hr_category = 'Low'
                max_hr_rate = 0.81
            elif max_hr < 140:
                max_hr_category = 'Middle'
                max_hr_rate = 0.64
            else:
                max_hr_category = 'High'
                max_hr_rate = 0.38
    
            #score prediction
            score = ((age_rate + gender_rate + pain_type_rate + chol_rate + max_hr_rate)/5)   
            return(redirect(url_for("count", min=(score), aa=(age_category), a=(age_rate), gg=(gender), g=(gender_rate), pp=(pain_type), p=(pain_type_rate), cc=(cholesterol_risk), c=(chol_rate), hh=(max_hr_category), h=(max_hr_rate), s=(stroke))))
        else:
            return '''<form action="main" method="POST">
                        <h1> Heart Failure Prediction </h1>
                        <h3> Age </h3>
                        <input name = "age">
                        <h3> Gender </h3>
                        <input name = "sex">
                        <h3> Chest Pain Type </h3>
                        <input name = "chest_pain_type">
                        <h3> Cholesterol </h3>
                        <input name = "cholesterol">
                        <h3> Max Heart Rate </h3>
                        <input name = "max_hr">
                        <input type="submit"/></form>'''
    else:
        return redirect(url_for("login"))

@app.route("/<min>,<a>,<aa>,<g>,<gg>,<p>,<pp>,<c>,<cc>,<h>,<hh>,<s>")
def count(min,a,aa,g,gg,p,pp,c,cc,h,hh,s):
    return jsonify({'a. PREDICTION SCORE' : f'{min}',
                    'b. Age'                      : f'{aa}',
                    'c. Age Score'                : f'{a}',
                    'd. Gender'                   : f'{gg}',
                    'e. Gender Score'             : f'{g}',
                    'f. Chest Pain Type'          : f'{pp}',
                    'g. Chest Pain Type Score'    : f'{p}',
                    'h. Cholesterol Risk'         : f'{cc}',
                    'i. Cholesterol Score'        : f'{c}',
                    'j. Maximum Heart Rate Level' : f'{hh}',
                    'k. Maximum Heart Rate Score' : f'{h}',
                    'STROKE TO HEART FAILURE RATIO' : f'{s}'}) 

@app.route("/logout")
def logout():
    session.pop("main", None)
    return '''<h3> Logged Out <h3>
            <a href="login"><button> Login </button></a>'''

if __name__ == '__main__':
    app.run(debug=True)