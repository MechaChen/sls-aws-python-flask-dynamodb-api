import os

import boto3
from flask import Flask, jsonify, make_response, request

app = Flask(__name__)


dynamodb_client = boto3.client('dynamodb')

if os.environ.get('IS_OFFLINE'):
    dynamodb_client = boto3.client(
        'dynamodb', region_name='localhost', endpoint_url='http://localhost:8000'
    )


USERS_TABLE = os.environ['USERS_TABLE']


@app.route('/users/<string:user_id>')
def get_user(user_id):
    result = dynamodb_client.get_item(
        TableName=USERS_TABLE, Key={'userId': {'S': user_id}}
    )
    item = result.get('Item')
    if not item:
        return jsonify({'error': 'Could not find user with provided "userId"'}), 404

    return jsonify(
        {'userId': item.get('userId').get('S'), 'name': item.get('name').get('S')}
    )


@app.route('/records', methods=['POST'])
def create_record():
    student_id = request.json.get('student_id')
    course = request.json.get('course')
    year = request.json.get('year')
    grade = request.json.get('grade')

    if (not student_id or not course or not year or not grade):
        return jsonify({
            'error': 'Please provide both "student_id", "course", "year" and "grade"'
        }), 400

    dynamodb_client.put_item(
        TableName=USERS_TABLE,
        Item={
            'student_id': {'S': student_id},
            'course': {'S': course},
            'year': {'S': year},
            'grade': {'S': grade}
        }
    )

    return jsonify({
        'student_id': student_id,
        'course': course,
        'year': year,
        'grade': grade
    })


@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error='Not found!'), 404)