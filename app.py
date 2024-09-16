from flask import Flask, render_template, redirect, url_for, request, session, jsonify
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.secret_key = '4321'
socketio = SocketIO(app)

# Dictionary to store current page status
page_status = {
    'current_page': 'page1'
}

# Admin credentials
admin_credentials = {
    'username': 'David',
    'password': '1234'  # Change this to a strong password
}

# Route for the main page where users see current content


@app.route('/')
def main():
    return render_template('main.html')

# API endpoint to return content only (without full layout)


@app.route('/content/<page>')
def get_page_content(page):
    if page in ['page1', 'page2']:
        return render_template(f'{page}.html')
    return jsonify({"error": "Page not found"}), 404

# Admin login page


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == admin_credentials['username'] and password == admin_credentials['password']:
            session['logged_in'] = True
            return redirect(url_for('control'))
        else:
            return render_template('admin.html', error='Invalid credentials')

    return render_template('admin.html')

# Admin control panel to switch between pages


@app.route('/control', methods=['GET', 'POST'])
def control():
    if not session.get('logged_in'):
        return redirect(url_for('admin'))

    if request.method == 'POST':
        page_status['current_page'] = request.form['page']
        # Emit a message to update all connected clients
        socketio.emit('page_change', {'new_page': page_status['current_page']})
        return redirect(url_for('control'))

    return render_template('control.html', current_page=page_status['current_page'])

# Logout route for admin


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('main'))


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
