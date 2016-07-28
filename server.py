from flask import Flask, render_template, request, redirect, session
import pg
import datetime

db = pg.DB('chirp_db')
app = Flask('ChirpApp')

@app.route('/')
def home():
    if 'username' in session:
        return redirect('/timeline')
    else:
        return render_template('login.html')

@app.route('/signup')
def signup():
    # show signup page
    return render_template(
        'signup.html',
        title='Sign up'
    )

@app.route('/submit_signup', methods=['POST'])
def submit_signup():
    # get the input info
    name = request.form['name']
    username = request.form['username']
    password = request.form['password']
    # insert new user to db
    db.insert('users', name=name, username=username, password=password)
    # send to login page to verify
    return redirect('/login')

@app.route('/login')
def login():
    # show login page
    return render_template(
        'login.html',
        title='Login'
    )

@app.route('/submit_login', methods=['POST'])
def submit_login():
    # get input info
    username = request.form['username']
    password = request.form['password']
    # query into db to check username
    query = db.query("select users.username from users where username = $1", username)
    dictionaried_result = query.dictresult()
    if len(dictionaried_result) > 0:
        session['username'] = username
        return redirect('/timeline')
    else:
        return redirect('/signup')


@app.route('/timeline')
def timeline():
    # query to find chirp info
    query = db.query('''
    select
    	users.name,
    	users.username,
    	chirp.chirp_content,
    	chirp.chirp_date
    from
    	chirp
    left outer join
    	users on chirp.user_id = users.id
    where
    	chirp.user_id = 1 or chirp.user_id in
    	(select
    		following_id
    	from
    		follow
    	where
    		follow.follower_id = 1)
    order by
    	chirp.chirp_date desc
    ''')
    # get query values as list of named tuples
    chirps = query.namedresult()
    # render to timeline page
    return render_template(
        'timeline.html',
        title='timeline',
        chirps=chirps
    )


@app.route('/profile')
def user_profile():
    # query to find chirp info
    query = db.query('''
    select
    	users.name,
    	users.username,
    	chirp.chirp_content,
    	chirp.chirp_date
    from
    	chirp
    left outer join
    	users on chirp.user_id = users.id
    where
    	users.id = 1
    order by
    	chirp.chirp_date desc
    ''')
    # get query values as list of named tuples
    chirps = query.namedresult()
    # render to profile page
    return render_template(
        'profile.html',
        title='profile',
        chirps=chirps
    )

# add chirps
@app.route('/chirps', methods=['POST'])
def submit_chirp():
    # get chirp input
    chirp_content = request.form['new_chirp']
    # add timestamp
    time = datetime.datetime.now()
    # insert it into db
    db.insert('chirp', user_id=1, chirp_date=time, chirp_content=chirp_content)
    return redirect('/timeline')


# secret key for sessions
app.secret_key = 'CSF686CCF85C6FRTCHQDBJDXHBHC1G478C86GCFTDCR'

app.debug = True

if __name__ == '__main__':
    app.run(debug=True)
