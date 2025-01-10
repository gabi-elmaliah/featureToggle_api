from flask import request, jsonify, Blueprint
from database.connection import MongoConnectionHolder
from datetime import datetime
import uuid

feature_toggle_blueprint = Blueprint('feature_toggle', __name__)


# 1. Create a new feature toggle
@feature_toggle_blueprint.route('/feature-toggle', methods=['POST'])
def create_feature_toggle():
    """
    Create a new feature toggle
    ---
    parameters:
        - name: feature_toggle
          in: body
          required: true
          description: The feature toggle to create
          schema:
            id: feature_toggle
            required:
                - package_name
                - name
                - description
                - beginning_date
                - expiration_date
            properties:
                package_name:
                    type: string
                    description: The name of the package
                name:
                    type: string
                    description: The name of the feature
                description:
                    type: string
                    description: The description of the feature toggle
                beginning_date:
                    type: string
                    description: The start date of the feature toggle
                expiration_date:
                    type: string
                    description: The end date of the feature toggle
    responses:
        201:
            description: The feature toggle was created successfully
        400:
            description: The request was invalid
        500:
            description: An error occurred while creating the feature toggle
    """
    data = request.json
    db = MongoConnectionHolder.get_db()

    # Check if the database connection was successful
    if db is None:
        return jsonify({"error": "Could not connect to the database"}), 500

    # Check if the request is valid
    if not all(key in data for key in ['package_name', 'name', 'description', 'beginning_date', 'expiration_date']):
        return jsonify({"error": "Invalid request"}), 400

    # Check data is valid
    try:
        # Parse the dates
        beginning_date = datetime.strptime(
            data['beginning_date'], '%Y-%m-%d %H:%M:%S')
        expiration_date = datetime.strptime(
            data['expiration_date'], '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD HH:MM:SS"}), 400

    if beginning_date > expiration_date:
        return jsonify({"error": "Beginning date must be before expiration date"}), 400

    # Create the feature toggle item
    feature_toggle_item = {
        "_id": str(uuid.uuid4()),
        "name": data['name'],
        "description": data['description'],
        "beginning_date": beginning_date,
        "expiration_date": expiration_date,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }

    # Insert the feature toggle into the database
    package_collection = db[data['package_name']]
    package_collection.insert_one(feature_toggle_item)

    return jsonify({"message": "Feature toggle created successfully", '_id': feature_toggle_item['_id']}), 201







