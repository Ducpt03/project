@app.route('/authenticator/dashboard')
def authenticator_dashboard():
    if 'email' not in session or session['role'] != 'authenticator':
        return redirect(url_for('home'))
    return render_template('authenticator.html')

@app.route('/authenticator/register', methods=['POST'])
def register_user():
    if 'email' not in session or session['role'] != 'authenticator':
        return redirect(url_for('home'))

    username = request.form['username']
    password = request.form['password']
    role = request.form['role']

    response = requests.post(f"{app.config['AUTHENTICATOR_URL']}/register", json={
        'username': username,
        'password': password,
        'role': role
    })

    if response.status_code == 200:
        flash('User registered successfully!', 'success')
    else:
        flash('Failed to register user!', 'danger')

    return redirect(url_for('authenticator_dashboard'))


@app.route('/data_owner/dashboard')
def data_owner_dashboard():
    if 'email' not in session or session['role'] != 'data_owner':
        return redirect(url_for('home'))
    return render_template('data_owner.html')

@app.route('/data_owner/upload', methods=['POST'])
def upload_file():
    if 'email' not in session or session['role'] != 'data_owner':
        return redirect(url_for('home'))

    file = request.files['file']
    owner = session['username']
    
    files = {'file': file}
    data = {'owner': owner}

    response = requests.post(f"{app.config['DATA_OWNER_URL']}/upload", files=files, data=data)

    if response.status_code == 200:
        flash('File uploaded successfully!', 'success')
    else:
        flash('Failed to upload file!', 'danger')

    return redirect(url_for('data_owner_dashboard'))

@app.route('/data_owner/grant_permission', methods=['POST'])
def grant_permission():
    if 'username' not in session or session['role'] != 'data_owner':
        return redirect(url_for('home'))

    file_name = request.form['file_name']
    user = request.form['user']

    response = requests.post(f"{app.config['DATA_OWNER_URL']}/grant_permission", json={
        'file_name': file_name,
        'user': user
    })

    if response.status_code == 200:
        flash('Permission granted successfully!', 'success')
    else:
        flash('Failed to grant permission!', 'danger')

    return redirect(url_for('data_owner_dashboard'))

@app.route('/data_user/dashboard')
def data_user_dashboard():
    if 'username' not in session or session['role'] != 'data_user':
        return redirect(url_for('home'))
    return render_template('data_user.html')

@app.route('/data_user/query', methods=['POST'])
def query_data():
    if 'username' not in session or session['role'] != 'data_user':
        return redirect(url_for('home'))

    file_name = request.form['file_name']
    user = session['username']

    response = requests.post(f"{app.config['DATA_USER_URL']}/query", json={
        'file_name': file_name,
        'user': user
    })

    if response.status_code == 200:
        result = response.json()
        flash(f"Data found: {result.get('content')}", 'success')
    else:
        flash('Failed to query data!', 'danger')

    return redirect(url_for('data_user_dashboard'))
