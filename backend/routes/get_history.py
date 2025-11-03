# backend/routes/get_history.py

from flask import Blueprint, jsonify
import csv
import os

get_history = Blueprint('get_history', __name__)

HISTORY_FILE = 'backend/logs/prediction_history.csv'

@get_history.route('/api/history', methods=['GET'])
def fetch_history():
    if not os.path.exists(HISTORY_FILE):
        return jsonify({'history': []})

    history_data = []
    try:
        with open(HISTORY_FILE, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                history_data.append(row)
    except Exception as e:
        return jsonify({'error': f'Failed to read history: {str(e)}'}), 500

    return jsonify({'history': history_data})
