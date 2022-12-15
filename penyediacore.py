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

    if auth and auth.username == 'username' and auth.password == 'pass':
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
            cholesterol = int(request.form['cholesterol'])
            max_hr = int(request.form['max_hr'])

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
            score = ((age_rate + gender_rate + chol_rate + max_hr_rate)/4)   
            return(redirect(url_for("count", min=(score), aa=(age_category), a=(age_rate), gg=(gender), g=(gender_rate), cc=(cholesterol_risk), c=(chol_rate), hh=(max_hr_category), h=(max_hr_rate))))
        else:
            return '''<form action="main" method="POST">
                        <h1> Heart Failure Prediction </h1>
                        <h3> Age </h3>
                        <input name = "age">
                        <h3> Gender </h3>
                        <input name = "sex">
                        <h3> Cholesterol </h3>
                        <input name = "cholesterol">
                        <h3> Max Heart Rate </h3>
                        <input name = "max_hr">
                        <input type="submit"/></form>'''
    else:
        return redirect(url_for("login"))

@app.route("/<min>,<a>,<aa>,<g>,<gg>,<c>,<cc>,<h>,<hh>")
def count(min,a,aa,g,gg,c,cc,h,hh):
    return jsonify({'1. PREDICTION SCORE' : f'{min}',
                    '2. Age'                      : f'{aa}',
                    '3. Age Score'                : f'{a}',
                    '4. Gender'                   : f'{gg}',
                    '5. Gender Score'             : f'{g}',
                    '6. Cholesterol Risk'         : f'{cc}',
                    '7. Cholesterol Score'        : f'{c}',
                    '8. Maximum Heart Rate Level' : f'{hh}',
                    '9. Maximum Heart Rate Score' : f'{h}'})

@app.route("/logout")
def logout():
    session.pop("main", None)
    return '''<h3> Logged Out <h3>
            <a href="login"><button> Login </button></a>'''

if __name__ == '__main__':
    app.run(debug=True)