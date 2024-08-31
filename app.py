from flask import Flask, request, redirect, session, render_template
from google_auth_oauthlib.flow import Flow
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Ensure you set up OAuth 2.0 configurations properly here

@app.route('/')
def index():
    return redirect('/index')

@app.route('/authorize')
def authorize():
    flow = Flow.from_client_secrets_file(
        'credentials.json',
        scopes=['https://www.googleapis.com/auth/calendar'],
        redirect_uri='https://localhost:5000/callback'
    )
    authorization_url, state = flow.authorization_url()
    session['state'] = state
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    state = session.get('state')
    flow = Flow.from_client_secrets_file(
        'credentials.json',
        scopes=['https://www.googleapis.com/auth/calendar'],
        redirect_uri='https://localhost:5000/callback'
    )
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    # Save the credentials for future use
    # You might want to save credentials to a session or database here
    return render_template('homepage.html', authenticated=True)

@app.route('/index')
def homepage():
    # Render the homepage template with the authenticated status
    return render_template('homepage.html', authenticated=False)

if __name__ == '__main__':
    app.run(ssl_context=('cert.pem', 'key.pem'), host='0.0.0.0', port=5000)
