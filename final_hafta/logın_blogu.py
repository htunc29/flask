@app.route('/login', methods=['GET', 'POST'])  #logın form ıcınden 
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)    #kullanıcıyı gırıs yapmıs olarak ısaretle.
            return redirect(url_for('dashboard'))  #dashboard a dondur. dashboard ıcınde ılgılı yerde user gırırsı gosterır.
        flash('E-posta veya şifre hatalı!', 'danger')
    return render_template('login.html')

