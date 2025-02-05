from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from _datetime import datetime

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)


@app.route('/messages', methods=['GET'])
def messages():
    # Query all messages and order them by created_at in ascending order
    messages = Message.query.order_by(Message.created_at.asc()).all()
    messages_list = [message.to_dict() for message in messages]
    return jsonify(messages_list)

@app.route('/messages', methods=['POST'])
def create_message():
    # Get data from the request body
    data = request.get_json()

    # Ensure both 'body' and 'username' are provided
    if not data.get('body') or not data.get('username'):
        return jsonify({'error': 'Both "body" and "username" are required.'}), 400

    # Create a new Message object
    new_message = Message(
        body=data['body'],
        username=data['username'],
        created_at=datetime.utcnow(),  
        updated_at=datetime.utcnow()   
    )

    db.session.add(new_message)
    db.session.commit()
    return jsonify(new_message.to_dict()), 201

@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    message = db.session.get(Message, id)
    
    if not message:
        return jsonify({'error': 'Message not found'}), 404
    
    data = request.get_json()
    
    if data.get('body'):
        message.body = data['body']
    
    message.updated_at = datetime.utcnow()

    db.session.commit()

    return jsonify(message.to_dict()), 200


@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = db.session.get(Message, id)
    
    if not message:
        return jsonify({'error': 'Message not found'}), 404
    
    db.session.delete(message)
    db.session.commit()

    return jsonify({'message': f'Message with id {id} has been deleted'}), 200

if __name__ == '__main__':
    app.run(port=5555)
