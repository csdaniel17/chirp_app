from flask import Flask, render_template, request, redirect, session
import pg
import datetime
import bcrypt

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
    password = request.form['password'].encode('utf-8')
    hashed = bcrypt.hashpw(password, bcrypt.gensalt())
    # insert new user to db
    db.insert('users', name=name, username=username, password=hashed)
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
    password = request.form['password'].encode('utf-8')
    hashed = db.query('''
        select
            users.password
        from
            users
        where
            users.username = $1
    ''', username).dictresult()[0]['password']
    if bcrypt.hashpw(password, hashed) == hashed:
        print("It Matches!")
    else:
        print("It Does not Match :(")


    # query into db to check username
    query = db.query("select users.id from users where username = $1", username)
    dictionaried_result = query.dictresult()
    user_id = dictionaried_result[0]['id']
    if len(dictionaried_result) > 0:
        session['username'] = username
        session['user_id'] = user_id
        print session['user_id']
        return redirect('/timeline')
    else:
        return redirect('/signup')


@app.route('/timeline')
def timeline():
    if not 'user_id' in session:
        # query all chirps
        query = db.query('''
        select
            users.name,
        	users.username,
            chirp.chirp_date,
            chirp.chirp_content
        from
            chirp
        left outer join
        	users on chirp.user_id = users.id
        order by
            chirp_date desc
        ''')
        chirps = query.namedresult()
    # query to find chirp info
    else:
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
        	chirp.user_id = $1 or chirp.user_id in
        	(select
        		following_id
        	from
        		follow
        	where
        		follow.follower_id = $1)
        order by
        	chirp.chirp_date desc
        ''', session['user_id'])
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
    if not 'user_id' in session:
        return redirect('/login')
    else:
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
        	users.username = $1
        order by
        	chirp.chirp_date desc
        ''', session['username'])
        # get query values as list of named tuples
        chirps = query.namedresult()
        bio_info = db.query('''
        select
            users.name,
            users.username
        from
            users
        where
            users.username = $1
        ''', session['username']).namedresult()
        print bio_info
        # render to profile page
        return render_template(
            'profile.html',
            title='profile',
            bio=bio_info,
            chirps=chirps
        )

# add chirps
@app.route('/chirps', methods=['POST'])
def submit_chirp():
    # get chirp input
    chirp_content = request.form['new_chirp']
    # get username
    username = session['username']
    query = db.query('''
        select
            users.id
        from
            users
        where
            users.username = $1
    ''', username)
    user_id = query.namedresult()[0].id
    # add timestamp
    time = datetime.datetime.now()
    # insert it into db
    db.insert('chirp', user_id=user_id, chirp_date=time, chirp_content=chirp_content)
    return redirect('/timeline')


# logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# secret key for sessions
app.secret_key = 'CSF686CCF85C6FRTCHQDBJDXHBHC1G478C86GCFTDCR'

app.debug = True

if __name__ == '__main__':
    app.run(debug=True)
