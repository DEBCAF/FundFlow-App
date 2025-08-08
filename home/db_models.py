from home import db, login_manager, app
from datetime import datetime
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    goals = db.relationship('Goal', backref='owner', lazy=True)
    
    def __repr__(self):
        return f"User('{self.username}','{self.email}','{self.image_file}')"
    
    def get_reset_token(self) -> str:
        s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        # Returns a string token
        return s.dumps({'user_id': self.id})
    
    @staticmethod
    def verify_reset_token(token: str, max_age: int = 1800):
        s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token, max_age=max_age)
            user_id = data['user_id']
        except Exception:
            return None
        return User.query.get(user_id)

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.Text, nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    deadline = db.Column(db.DateTime, nullable=True)
    category = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='active')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
