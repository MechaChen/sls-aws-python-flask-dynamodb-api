import os

import boto3
from boto3.dynamodb.conditions import Key, Attr
from flask import Flask, jsonify, make_response, request

app = Flask(__name__)


dynamodb_client = boto3.client('dynamodb')
dynamodb_resource = boto3.resource('dynamodb')

if os.environ.get('IS_OFFLINE'):
    dynamodb_client = boto3.client(
        'dynamodb', region_name='localhost', endpoint_url='http://localhost:8000'
    )


USERS_TABLE = os.environ['USERS_TABLE']
records_table = dynamodb_resource.Table(USERS_TABLE)


@app.route('/records', methods=['GET'])
def get_records():
    year = request.args.get('year')
    student_id = request.args.get('student_id')
    course = request.args.get('course')

    result = None

    if (student_id and year):
        result = records_table.query(
            IndexName='year-index',
            KeyConditionExpression=Key('student_id').eq(student_id) & Key('year').eq(year)
        )

    if (year and course):
        result = records_table.query(
            IndexName='course-year-index',
            KeyConditionExpression=Key('course').eq(course) & Key('year').eq(year)
        )

    items = result['Items']
    return jsonify(items)



@app.route('/record', methods=['GET'])
def get_record():
    student_id = request.args.get('student_id')
    course = request.args.get('course')

    result = dynamodb_client.get_item(
        TableName=USERS_TABLE,
        Key={
            'student_id': {'S': student_id},
            'course': {'S': course}
        }
    )

    item = result.get('Item')

    if not item:
        return jsonify({'error': 'Could not find user with provided "student_id" and "course"'}), 404

    return jsonify(
        {
            'student_id': item.get('student_id').get('S'),
            'course': item.get('course').get('S'),
            'year': item.get('year').get('S'),
        }
    )


@app.route('/record', methods=['POST'])
def create_record():
    student_id = request.json.get('student_id')
    course = request.json.get('course')
    year = request.json.get('year')

    if (not student_id or not course or not year):
        return jsonify({
            'error': 'Please provide both "student_id", "course" and "year"'
        }), 400

    dynamodb_client.put_item(
        TableName=USERS_TABLE,
        Item={
            'student_id': {'S': student_id},
            'course': {'S': course},
            'year': {'S': year},
        }
    )

    return jsonify({
        'student_id': student_id,
        'course': course,
        'year': year,
    })


@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error='Not found!'), 404)