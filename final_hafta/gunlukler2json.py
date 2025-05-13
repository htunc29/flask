from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import json
from flask_login import UserMixin

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

# Modeller
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Gunluk(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    baslik = db.Column(db.String(150), nullable=False)
    icerik = db.Column(db.Text, nullable=False)
    kategori = db.Column(db.String(50), nullable=False)
    kullanici_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('gunlukler', lazy=True))

# JSON'a aktarım fonksiyonu
def export_gunlukler_to_json():
    with app.app_context():
        gunlukler = Gunluk.query.all()
        data = []
        for gunluk in gunlukler:
            data.append({
                'id': gunluk.id,
                'baslik': gunluk.baslik,
                'icerik': gunluk.icerik,
                'kategori': gunluk.kategori,
                'kullanici_id': gunluk.kullanici_id,
                'kullanici_adi': gunluk.user.name if gunluk.user else None
            })

        with open('gunlukler.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        print("Günlükler başarıyla gunlukler.json dosyasına kaydedildi!")

# Ana fonksiyon
if __name__ == '__main__':
    export_gunlukler_to_json()
