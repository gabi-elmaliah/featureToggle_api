from flask import request, jsonify, Blueprint
from database.connection import MongoConnectionHolder
from datetime import datetime,timezone,timedelta
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
                -id
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


@feature_toggle_blueprint.route('/feature-toggles/<package_name>', methods=['GET'])
def get_all_features_for_package(package_name):
    """
    Retrieve all feature toggles for a specific package
    ---
    parameters:
      - name: package_name
        in: path
        type: string
        required: true
        description: The name of the package
    responses:
      200:
        description: Successfully retrieved feature toggles
    schema:
      type: array
      items:
        type: object
        properties:
          name:
            type: string
            description: The name of the feature
          description:
            type: string
            description: The description of the feature
          beginning_date:
            type: string
            description: The start date of the feature
          expiration_date:
            type: string
            description: The expiration date of the feature
          created_at:
                type: string
                description: The creation date of the feature
          updated_at:
                type: string
                description: The last updated date of the feature

         
      500:
        description: An error occurred while retrieving feature toggles
      404:
        description: The specified package does not exist
    """
    db = MongoConnectionHolder.get_db()
    if db is None:
        return jsonify({"error": "Could not connect to the database"}), 500
    
    if package_name not in db.list_collection_names():
        return jsonify({"error": f"Package '{package_name}' does not exist"}), 404
    

    
    try:
        collection = db[package_name]
        feature_toggles = list(collection.find({}))  
        return jsonify(feature_toggles), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred"}), 500


#  Get all active feature toggles for package name and date
@feature_toggle_blueprint.route('/feature-toggles/<package_name>/by-date', methods=['GET'])
def get_feature_toggles_by_date(package_name):
    """
    Get all active feature toggles by a specific date
    --- 
    parameters:
        - name: package_name
          in: path
          type: string
          required: true
          description: Name of the package
        - name: date
          in: query
          type: string
          required: true
          description: Date in the format YYYY-MM-DD
    responses:
        200:
            description: List of active feature toggles by date
        404:
            description: The specified package does not exist
        500:
            description: An error occurred while retrieving feature toggles
    """
    date_str = request.args.get('date', "")
    db = MongoConnectionHolder.get_db()
    if db is None:
        # Helpful error message for debugging
        return jsonify({'error': 'Database not initialized'}), 500
    
    if package_name not in db.list_collection_names():
        return jsonify({"error": f"Package '{package_name}' does not exist"}), 404
    

    try:
        # Parse specific date
        specific_date = datetime.strptime(date_str, '%Y-%m-%d')
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid date format, use YYYY-MM-DD'}), 400

    features_by_date = []
    package_collection = db[package_name]

    # Find feature toggles by date
    active_features_by_date = list(package_collection.find({
        'expiration_date': {'$gte': specific_date},
        'beginning_date': {'$lte': specific_date}
    }))
    for feature in active_features_by_date:
        features_by_date.append(feature)
    return jsonify(features_by_date), 200


#  Delete all feature toggles for package name
@feature_toggle_blueprint.route('/feature-toggles/<package_name>', methods=['DELETE'])
def delete_all_feature_toggles(package_name):
    """
    Delete all feature toggles
    --- 
    parameters:
        - name: package_name
          in: path
          type: string
          required: true
          description: Name of the package
    responses:
        200:
            description: All feature toggles deleted
        404:
            description: Package not found
    """
    db = MongoConnectionHolder.get_db()
    if db is None:
        return jsonify({"error": "Could not connect to the database"}), 500
    
    if package_name not in db.list_collection_names():
        return jsonify({"error": f"Package '{package_name}' does not exist"}), 404
    
    package_collection = db[package_name]
    
    # Delete all feature toggles
    package_collection.delete_many({})
    return jsonify({'message': 'All feature toggles deleted'}), 200




    

@feature_toggle_blueprint.route('/feature-toggles/<package_name>/active', methods=['GET'])
def get_active_features(package_name):

    """
    Retrieve all active feature toggles for a specific package
    ---
    parameters:
      - name: package_name
        in: path
        type: string
        required: true
        description: The name of the package
    responses:
      200:
        description: Successfully retrieved active feature toggles
        schema:
          type: array
          items:
            type: object
            properties:
              name:
                type: string
                description: The name of the feature
              description:
                type: string
                description: The description of the feature
              beginning_date:
                type: string
                description: The start date of the feature
              expiration_date:
                type: string
                description: The expiration date of the feature
              created_at:
                type: string
                description: The creation date of the feature
              updated_at:
                type: string
                description: The last updated date of the feature

      404:
        description: The specified package does not exist
      500:
        description: An error occurred while retrieving active feature toggles
    """

    db = MongoConnectionHolder.get_db()
    if db is None:
        return jsonify({"error": "Could not connect to the database"}), 500
    
    if package_name not in db.list_collection_names():
        return jsonify({"error": f"Package '{package_name}' does not exist"}), 404
    
    try:
        # Query the collection for all active features
        current_time = datetime.now(timezone.utc)
        collection = db[package_name]
        active_features = list(collection.find({
            "beginning_date": {"$lte": current_time},
            "expiration_date": {"$gte": current_time}}))  

        return jsonify(active_features), 200
    except Exception as e:
        return jsonify({"error": "An error occurred while retrieving active feature toggles"}), 500
    
@feature_toggle_blueprint.route('/feature-toggles/<package_name>/<feature_id>', methods=['DELETE'])
def delete_feature_toggle(package_name, feature_id):

    """
    Delete a specific feature toggle within a package by its `_id`
    ---
    parameters:
      - name: package_name
        in: path
        type: string
        required: true
        description: The name of the package containing the feature toggle
      - name: feature_id
        in: path
        type: string
        required: true
        description: The `_id` of the feature toggle to delete
    responses:
      200:
        description: Successfully deleted the feature toggle
      404:
        description: Package or feature not found
      400:
        description: Invalid feature_id format
      500:
        description: An error occurred while deleting the feature toggle
    """
    db = MongoConnectionHolder.get_db()

    # Validate database connection
    if db is None:
        return jsonify({"error": "Could not connect to the database"}), 500

    # Check if the package_name collection exists
    if package_name not in db.list_collection_names():
        return jsonify({"error": f"Package '{package_name}' does not exist"}), 404
    
    try:
        collection = db[package_name]
        # Attempt to delete the feature toggle by string `_id`
        result = collection.delete_one({"_id": feature_id})

        # Check if a document was deleted
        if result.deleted_count == 0:
            return jsonify({"error": f"Feature with _id '{feature_id}' does not exist in package '{package_name}'"}), 404
        
        return jsonify({"message": f"Feature with _id '{feature_id}' successfully deleted from package '{package_name}'"}), 200
    except Exception as e:
        print(f"Error deleting feature with _id '{feature_id}' in package '{package_name}': {e}")
        return jsonify({"error": "An error occurred while deleting the feature toggle"}), 500
    
    

@feature_toggle_blueprint.route('/feature-toggles/<package_name>/<feature_id>/update-dates', methods=['PUT'])
def update_feature_toggle(package_name, feature_id):
    """
    Update the beginning and expiration dates of a feature toggle
    --- 
    parameters:
        - name: package_name
          in: path
          type: string
          required: true
          description: Name of the package
        - name: feature_id
          in: path
          type: string
          required: true
          description: ID of the feature toggle to update
        - name: updated_data
          in: body
          required: true
          description: The feature toggle to create
          schema:
              id: UpdatedData
              optional:
              - expiration_date
              - beginning_date
              properties:
                expiration_date:
                  type: string
                  description: Expiration date of the feature toggle in the format YYYY-MM-DD HH:MM:SS
                beginning_date:
                  type: string
                  description: Beginning date of the feature toggle in the format YYYY-MM-DD HH:MM:SS
    responses:
        200:
            description: Dates updated
        400:
            description: Invalid date format
        404:
            description: Feature toggle not found
    """
    data = request.json
    new_expiration_date = None
    new_beginning_date = None
    db = MongoConnectionHolder.get_db()
    if db is None:
        # Helpful error message for debugging
        return jsonify({'error': 'Database not initialized'}), 500
    
    # Check if the package_name collection exists
    if package_name not in db.list_collection_names():
        return jsonify({"error": f"Package '{package_name}' does not exist"}), 404

    # Check for new dates in request data
    if 'expiration_date' in data:
        new_expiration_date = data.get('expiration_date')
    if 'beginning_date' in data:
        new_beginning_date = data.get('beginning_date')

    if not 'expiration_date' in data and not 'beginning_date' in data:
        return jsonify({'error': 'No dates provided'}), 400

    try:
        # Parse new dates
        if new_expiration_date:
            new_expiration_date = datetime.strptime(
                new_expiration_date, '%Y-%m-%d %H:%M:%S')
        if new_beginning_date:
            new_beginning_date = datetime.strptime(
                new_beginning_date, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return jsonify({'error': 'Invalid date format, use YYYY-MM-DD HH:MM:SS'}), 400

    if new_beginning_date and new_expiration_date and new_beginning_date > new_expiration_date:
        return jsonify({'error': 'Beginning date must be before expiration date'}), 400

    package_collection = db[package_name]
   
    # Find and update feature toggle
    feature = package_collection.find_one({'_id': feature_id})
    if feature:
        if new_expiration_date:
            if new_expiration_date < feature['beginning_date']:
                return jsonify({'error': 'Expiration date cannot be before beginning date'}), 400
            feature['expiration_date'] = new_expiration_date
        if new_beginning_date:
            if new_beginning_date > feature['expiration_date']:
                return jsonify({'error': 'Beginning date cannot be after expiration date'}), 400
            feature['beginning_date'] = new_beginning_date
        
        # Update the updated_at field
        feature['updated_at'] = datetime.now()

        package_collection.update_one(
            {'_id': feature['_id']},
            {'$set': feature}
        )
        return jsonify({'message': 'Dates updated'}), 200

    return jsonify({'error': 'Feature toggle not found'}), 404

@feature_toggle_blueprint.route('/feature-toggles/<package_name>/recent', methods=['GET'])
def get_recent_features(package_name):
    """
    Retrieve all feature toggles created in the last 30 days for a specific package
    ---
    parameters:
      - name: package_name
        in: path
        type: string
        required: true
        description: The name of the package containing the features
    responses:
      200:
        description: Successfully retrieved recent feature toggles
      404:
        description: Package not found
      500:
        description: An error occurred while retrieving feature toggles
    """

    db = MongoConnectionHolder.get_db()

    if db is None:
        return jsonify({'error': 'Database not initialized'}), 500
    
    # Check if the package_name collection exists
    if package_name not in db.list_collection_names():
        return jsonify({"error": f"Package '{package_name}' does not exist"}), 404
    
    # Calculate the date 30 days ago
    thirty_days_ago = datetime.now() - timedelta(days=30)

    try:
        package_collection = db[package_name]
        recent_features = list(package_collection.find(
            {"created_at": {"$gte": thirty_days_ago}},
            {"_id": 0}  # Exclude `_id` or include it depending on your preference
        ))

        return jsonify(recent_features), 200
    except Exception as e:
        print(f"Error retrieving recent features: {e}")
        return jsonify({"error": "An error occurred while retrieving recent features"}), 500
    
@feature_toggle_blueprint.route('/feature-toggles/<package_name>/<feature_id>/update-info', methods=['PUT'])
def update_feature_info(package_name, feature_id):
    """
    Update the name or description of a feature toggle
    ---
    parameters:
        - name: package_name
          in: path
          type: string
          required: true
          description: The name of the package
        - name: feature_id
          in: path
          type: string
          required: true
          description: The ID of the feature toggle to update
        - name: updated_data
          in: body
          required: true
          description: The feature toggle to create
          schema:
              optional:
              - name
              - description
              properties:
                name:
                  type: string
                  description: the name of the feature 
                description:
                  type: string
                  description: description of the feature 
    responses:
        200:
            description: Feature updated successfully
        404:
            description: Feature or package not found
        400:
            description: Invalid request data
    """

    data = request.json
    db = MongoConnectionHolder.get_db()

    if db is None:
        return jsonify({"error": "Database not initialized"}), 500

    # Check if the package_name collection exists
    if package_name not in db.list_collection_names():
        return jsonify({"error": f"Package '{package_name}' does not exist"}), 404

    package_collection = db[package_name]

    # Find the feature toggle
    feature = package_collection.find_one({"_id": feature_id})
    if not feature:
        return jsonify({"error": f"Feature toggle with ID '{feature_id}' not found"}), 404
    
    # Update fields
    updates = {}
    if 'name' in data and data['name']:
        updates['name'] = data['name']
    if 'description' in data and data['description']:
        updates['description'] = data['description']
    
    if not updates:
        return jsonify({"error": "No valid fields provided for update"}), 400

    # Add updated_at field
    updates['updated_at'] = datetime.now()

      # Update the feature in the database
    package_collection.update_one(
        {"_id": feature_id},
        {"$set": updates}
    )

    return jsonify({"message": "Feature updated successfully"}), 200


@feature_toggle_blueprint.route('/feature-toggles/<package_name>/active-in-range', methods=['GET'])
def get_active_features_in_range(package_name):

    """
Retrieve all active feature toggles within a specific date range for a package
---
parameters:
  - name: package_name
    in: path
    type: string
    required: true
    description: The name of the package containing the features
  - name: start_date
    in: query
    type: string
    required: true
    description: "The start date of the range (format: YYYY-MM-DD)"
  - name: end_date
    in: query
    type: string
    required: true
    description: "The end date of the range (format: YYYY-MM-DD)"
responses:
  200:
    description: Successfully retrieved active feature toggles
    content:
      application/json:
        schema:
          type: array
          items:
            type: object
            properties:
              name:
                type: string
                description: The name of the feature
              description:
                type: string
                description: The description of the feature
              beginning_date:
                type: string
                description: The start date of the feature
              expiration_date:
                type: string
                description: The expiration date of the feature
              created_at:
                type: string
                description: The creation date of the feature
              updated_at:
                type: string
                description: The last updated date of the feature
  400:
    description: Invalid query parameters
  404:
    description: Package not found
  500:
    description: Internal server error
"""

  
    db = MongoConnectionHolder.get_db()

    if db is None:
        return jsonify({'error': 'Database not initialized'}), 500
    
    # Check if the package_name collection exists
    if package_name not in db.list_collection_names():
        return jsonify({"error": f"Package '{package_name}' does not exist"}), 404
    
     # Get query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if not start_date or not end_date:
        return jsonify({"error": "Both 'start_date' and 'end_date' are required"}), 400
    
    try:
        # Parse dates
        start_date_parsed = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_parsed = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    # Check date range validity
    if start_date_parsed > end_date_parsed:
        return jsonify({"error": "Start date must be before end date"}), 400
    
    try:
        package_collection = db[package_name]

        # Query for active features in the date range
        active_features = list(package_collection.find(
            {
                "beginning_date": {"$lte": end_date_parsed},
                "expiration_date": {"$gte": start_date_parsed}
            }
        ))

        return jsonify(active_features), 200
    except Exception as e:
        print(f"Error retrieving active features in range: {e}")
        return jsonify({"error": "An error occurred while retrieving features"}), 500

@feature_toggle_blueprint.route('/feature-toggles/<package_name>/statistics', methods=['GET'])
def get_feature_statistics(package_name):
    """
    Retrieve feature usage statistics for a specific package
    ---
    parameters:
      - name: package_name
        in: path
        type: string
        required: true
        description: The name of the package containing the features
    responses:
      200:
        description: Successfully retrieved feature statistics
        content:
          application/json:
            schema:
              type: object
              properties:
                total_features:
                  type: integer
                  description: Total number of features in the package
                active_features:
                  type: integer
                  description: Number of currently active features
      404:
        description: Package not found
      500:
        description: Internal server error
    """
    db = MongoConnectionHolder.get_db()
    if db is None:
        return jsonify({'error': 'Database not initialized'}), 500

    # Check if the package_name collection exists
    if package_name not in db.list_collection_names():
        return jsonify({"error": f"Package '{package_name}' does not exist"}), 404
    
    collection = db[package_name]
    current_time = datetime.now()

    try:
        total_features = collection.count_documents({})
        active_features = collection.count_documents({
            "beginning_date": {"$lte": current_time},
            "expiration_date": {"$gte": current_time}
        })

        return jsonify({
            "total_features": total_features,
            "active_features": active_features
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

    
    













    







