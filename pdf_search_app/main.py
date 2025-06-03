import os
print("Running file:", os.path.abspath(__file__))


from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'password':
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid credentials. Please try again.'
    return render_template('login.html', error=error)


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # upload logic coming later
        return redirect(url_for('dashboard'))
    return render_template('upload.html')

@app.route('/results')
def search():
    # dummy results for now
    dummy_results = ["file1.pdf", "file2.pdf"]
    return render_template('results.html', results=dummy_results)

if __name__ == '__main__':
    print("Actually hitting the app.run() line")
    app.run(port=5001, debug=False, use_reloader=False)

