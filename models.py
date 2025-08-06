from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# ------------------- User Model -------------------
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    # Relationships
    files = db.relationship('File', backref='owner', lazy=True)
    recycle_files = db.relationship('RecycleBin', backref='user', lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"


# ------------------- File Model -------------------
class File(db.Model):
    __tablename__ = 'files'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.Text, nullable=False)
    filepath = db.Column(db.Text, nullable=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    file_code = db.Column(db.String(100), unique=True, nullable=False)
    tags = db.Column(db.String(255), nullable=True)
    cabinet = db.Column(db.String(100), nullable=True)
    shelf = db.Column(db.String(100), nullable=True)
    box = db.Column(db.String(100), nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f"<File {self.filename}>"


# ------------------- Recycle Bin Model -------------------
class RecycleBin(db.Model):
    __tablename__ = 'recycle_bin'

    id = db.Column(db.Integer, primary_key=True)
    file_code = db.Column(db.String(100), nullable=False)
    filename = db.Column(db.Text, nullable=False)
    filepath = db.Column(db.Text, nullable=True)
    deleted_at = db.Column(db.DateTime, default=datetime.utcnow)

    # File metadata (preserved from File model)
    tags = db.Column(db.String(255), nullable=True)
    cabinet = db.Column(db.String(100), nullable=True)
    shelf = db.Column(db.String(100), nullable=True)
    box = db.Column(db.String(100), nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f"<RecycleBin File {self.filename}>"
