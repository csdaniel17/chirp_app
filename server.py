from flask import Flask, render_template, request, redirect, session
import pg

db = pg.DB('chirp_db')

app = Flask('ChirpApp')


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
    ''')
    # get query values as list of named tuples
    chirps = query.namedresult()
    # render to profile page
    return render_template(
        'profile.html',
        title='profile',
        chirps=chirps
    )

# secret key for sessions
app.secret_key = 'CSF686CCF85C6FRTCHQDBJDXHBHC1G478C86GCFTDCR'

app.debug = True

if __name__ == '__main__':
    app.run(debug=True)
