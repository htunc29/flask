from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gelistirme_anahtari' #sessıon bılgılerını tarayıcıda tutmak ıcın
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' #database ne adında olucak
db = SQLAlchemy(app)

login_manager = LoginManager(app)  #kullanıcı gereklı bır sayfa mevcut ıse: kısının gunluklerı gıbı
login_manager.login_view = 'login'  # gereklı gıurıs ıcın hangı rota kullanılsın? logın rotasına gıt

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    # Gunluk ile ilişkiyi sadece burada tanımlıyoruz:
    gunlukler = db.relationship('Gunluk', back_populates='kullanici')

class Gunluk(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    baslik = db.Column(db.String(150), nullable=False)
    icerik = db.Column(db.Text, nullable=False)
    kategori = db.Column(db.String(50), nullable=False)
    kullanici_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Kullanıcıya ters ilişki
    kullanici = db.relationship('User', back_populates='gunlukler')
    # ad / soyad / cinsiyet / adres / yas 


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

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

@app.route('/register', methods=['GET', 'POST']) #regıster form ıcınden 
def register():
    if request.method == 'POST': 
        email = request.form.get('email') #regıster formundan gelen emaıl
        password = request.form.get('password') #regıster formundan gelen password
        
        if User.query.filter_by(email=email).first():
            flash('Bu e-posta zaten kayıtlı!', 'danger') #sayfa mesajları dondurme
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        name = request.form.get('name') 
        new_user = User(name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Kayıt başarılı! Giriş yapabilirsiniz.', 'success') #sayfa mesajları dondurme
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/dashboard')
@login_required
def dashboard():
    gunlukler = Gunluk.query.filter_by(kullanici_id=current_user.id).order_by(Gunluk.id.desc()).all()
    return render_template('dashboard.html', gunlukler=gunlukler)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard/gunluk_ekle', methods=['GET', 'POST'])
@login_required
def gunluk_ekle():
    if request.method == 'POST':
        baslik = request.form.get('baslik')
        icerik = request.form.get('icerik')
        kategori = request.form.get('kategori')

        # Kullanıcı girişi kontrolü 
        if current_user.is_authenticated:
            yeni_gunluk = Gunluk(
                baslik=baslik,
                icerik=icerik,
                kategori=kategori,
                kullanici_id=current_user.id  # Doğru kullanıcı ID'si
            )
            db.session.add(yeni_gunluk)
            db.session.commit()

            flash('Günlük başarıyla kaydedildi!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Kullanıcı girişi yapılmamış!', 'danger')
            return redirect(url_for('login'))

    return render_template('gunluk_ekle.html')

@app.route('/gunluk/duzenle/<int:gunluk_id>', methods=['GET', 'POST'])
@login_required
def gunluk_duzenle(gunluk_id):
    gunluk = Gunluk.query.get_or_404(gunluk_id)
    
    # Eğer kullanıcı bu kayda ait değilse, yetkisiz erişim
    if gunluk.kullanici_id != current_user.id:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        gunluk.baslik = request.form['baslik']
        gunluk.icerik = request.form['icerik']
        gunluk.kategori = request.form['kategori']
        
        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('gunluk_duzenle.html', gunluk=gunluk)


@app.route('/gunluk/sil/<int:gunluk_id>', methods=['POST'])
@login_required
def gunluk_sil(gunluk_id):
    gunluk = Gunluk.query.get_or_404(gunluk_id)
    
    # Kullanıcının sadece kendi günlüklerini silebilmesi için kontrol
    if gunluk.kullanici_id != current_user.id:
        flash("Bu kaydı silemezsiniz!", "danger")
        return redirect(url_for('dashboard'))
    
    db.session.delete(gunluk)
    db.session.commit()
    flash("Günlük başarıyla silindi!", "success")
    return redirect(url_for('dashboard'))





#if __name__ == '__main__':
#    with app.app_context():
#        db.create_all()
#    app.run(debug=True)
import os

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
