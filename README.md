# Flask Feature Toggle API

This API provides functionality for managing feature toggles in a MongoDB-backed system. It allows developers to activate or deactivate features for specific packages dynamically, enabling flexible and efficient feature rollout strategies.

## Features

- **Feature Management**: Create, retrieve, update, and delete feature toggles.
- **Active Feature Query**: Fetch active features by date or date range.
- **Statistics**: Get usage statistics for a package.
- **MongoDB Integration**: Persistent feature toggle storage.
- **Flasgger Integration**: Interactive API documentation.

---

## Endpoints

### 1. Create a New Feature Toggle

**POST /feature-toggle**

**Description**: Creates a new feature toggle.

**Request Body**:

```json
{
  "package_name": "string",
  "name": "string",
  "description": "string",
  "beginning_date": "YYYY-MM-DD HH:MM:SS",
  "expiration_date": "YYYY-MM-DD HH:MM:SS"
}
```

**Responses:**

- **201:** Feature toggle created successfully.
- **400:** Invalid request or date format.
- **500:** Database connection error.

---

### 2. Get All Features for a Package

**GET /feature-toggles/{package_name}**

**Description**: Retrieves all feature toggles for the specified package.

#### Parameters

- **Path Parameters**:
  - `package_name` (string, required): The name of the package.

#### Responses

- **200**: Successfully retrieved feature toggles.

  **Body** (JSON Array):

  ```json
  [
    {
      "name": "string",
      "description": "string",
      "beginning_date": "YYYY-MM-DD HH:MM:SS",
      "expiration_date": "YYYY-MM-DD HH:MM:SS",
      "created_at": "YYYY-MM-DD HH:MM:SS",
      "updated_at": "YYYY-MM-DD HH:MM:SS"
    }
  ]
  ```

- **404**: Package not found.

  **Example**:

  ```json
  {
    "error": "Package 'example_package' does not exist"
  }
  ```

- **500:** Database connection error.

  **Body**:

  ```json
  {
    "error": "Could not connect to the database"
  }
  ```

---

### 3. Get All Active Feature Toggles for a Package by Date

**Endpoint**: `GET /feature-toggles/{package_name}/by-date`

**Description**: Retrieves all active feature toggles for a specific package on a given date. A feature toggle is considered active if the specified date falls within its `beginning_date` and `expiration_date`.

#### Parameters

- **Path Parameters**:
  - `package_name` (string, required): The name of the package.

- **Query Parameters**:
  - `date` (string, required): The specific date in the format `YYYY-MM-DD`.

#### Responses

- **200 OK**: Successfully retrieved active feature toggles for the specified date.

  **Body** (JSON Array):

  ```json
  [
    {
      "name": "string",
      "description": "string",
      "beginning_date": "YYYY-MM-DD HH:MM:SS",
      "expiration_date": "YYYY-MM-DD HH:MM:SS",
      "created_at": "YYYY-MM-DD HH:MM:SS",
      "updated_at": "YYYY-MM-DD HH:MM:SS"
    }
  ]
  ```

- **400 Bad Request**: Invalid query parameter (e.g., incorrect date format).

  **Body**:

  ```json
  {
    "error": "Invalid date format, use YYYY-MM-DD"
  }
  ```

- **404 Not Found**: The specified package does not exist.

  **Body**:

  ```json
  {
    "error": "Package 'example_package' does not exist"
  }
  ```

- **500 Internal Server Error**: A server or database connection error occurred.

  **Body**:

  ```json
  {
    "error": "Database not initialized"
  }
  ```

---

### 4. Delete All Feature Toggles for a Package

**Endpoint**: `DELETE /feature-toggles/{package_name}`

**Description**: Deletes all feature toggles for the specified package.

#### Parameters

- **Path Parameters**:
  - `package_name` (string, required): The name of the package whose feature toggles will be deleted.

#### Responses

- **200 OK**: Successfully deleted all feature toggles for the specified package.

  **Body**:

  ```json
  {
    "message": "All feature toggles deleted"
  }
  ```

- **404 Not Found**: The specified package does not exist.

  **Body**:

  ```json
  {
    "error": "Package 'example_package' does not exist"
  }
  ```

- **500 Internal Server Error**: A server or database connection error occurred.

  **Body**:

  ```json
  {
    "error": "Could not connect to the database"
  }
  ```

### 5. Get Active Features in the Package

**Endpoint**: `GET /feature-toggles/{package_name}/active`

**Description**: Retrieves all active feature toggles for the specified package.

#### Parameters

- **Path Parameters**:
  - `package_name` (string, required): The name of the package whose active feature toggles will be retrieved.

#### Responses

- **200 OK**: Successfully retrieved active feature toggles for the specified package.

 **Body** (JSON Array):

  ```json
  [
    {
      "name": "string",
      "description": "string",
      "beginning_date": "YYYY-MM-DD HH:MM:SS",
      "expiration_date": "YYYY-MM-DD HH:MM:SS",
      "created_at": "YYYY-MM-DD HH:MM:SS",
      "updated_at": "YYYY-MM-DD HH:MM:SS"
    }
  ]
  ```

  -**404 Not Found**: The specified package does not exist.

  **Body**:

  ```json
  {
    "error": "Package 'example_package' does not exist"
  }
  ```

- **500 Internal Server Error**: A server or database connection error occurred.

  **Body**:

  ```json
  {
    "error": "Could not connect to the database"
  }
  ```

  ### 6. Delete a Feature in the Given Package

**Endpoint**: `DELETE /feature-toggles/{package_name}/{feature_id}`

**Description**: Deletes a specific feature toggle within a package by its `_id`.

#### Parameters

- **Path Parameters**:
  - `package_name` (string, required): The name of the package containing the feature toggle.
  - `feature_id` (string, required): The `_id` of the feature toggle to delete.

  #### Responses

- **200 OK**: Successfully deleted the feature toggle.

  **Body**:

  ```json
  {
    "message": "Feature with _id 'feature_id' successfully deleted from package 'package_name'"
  }
  ```

- **400:** Invalid request or date format.
- **500:** Database connection error.

### 7. Update the beginning and expiration dates of a feature toggle

**Endpoint**: `PUT /feature-toggles/{package_name}/{feature_id}/update-dates`

**Description**: Updates the beginning and expiration dates of a specific feature toggle.

#### Parameters

- **Path Parameters**:
  - `package_name` (string, required): The name of the package containing the feature toggle.
  - `feature_id` (string, required): The ID of the feature toggle to update.

- **Body Parameters**:
  - `expiration_date` (string, optional): The new expiration date for the feature toggle in the format `YYYY-MM-DD HH:MM:SS`.
  - `beginning_date` (string, optional): The new beginning date for the feature toggle in the format `YYYY-MM-DD HH:MM:SS`.

#### Responses

- **200 OK**: Successfully updated the beginning and/or expiration dates of the feature toggle.
- **404 Not Found**: Invalid request or date format.
- **500 Internal Server Error**: A server or database connection error occurred.

### 8. Retrieve All Feature Toggles Created in the Last 30 Days for a Specific Package

**Endpoint**: `GET /feature-toggles/{package_name}/recent`

**Description**: Retrieves all feature toggles that were created in the last 30 days for a specified package.

#### Parameters

- **Path Parameters**:
  - `package_name` (string, required): The name of the package containing the features.

#### Responses

- **200 OK**: List of feature toggles.

  **Body** (JSON Array):

  ```json
  [
    {
      "name": "string",
      "description": "string",
      "beginning_date": "YYYY-MM-DD HH:MM:SS",
      "expiration_date": "YYYY-MM-DD HH:MM:SS",
      "created_at": "YYYY-MM-DD HH:MM:SS",
      "updated_at": "YYYY-MM-DD HH:MM:SS"
    }
  ]
  ```

- **404 Not Found**: Invalid request or date format.
- **500 Internal Server Error**: A server or database connection error occurred.

### 9.Update the name or description of a feature toggle

**Endpoint**: `PUT /feature-toggles/<package_name>/<feature_id>/update-info`

**Description**: Update the name and description of a feature toggle.

- **Path Parameters**:
  - `package_name` (string, required): The name of the package containing the feature toggle.
  - `feature_id` (string, required): The ID of the feature toggle to update.

#### Responses

- **200 OK**: Feature updated successfully
- **404 Not Found**: Invalid request or date format.
- **500 Internal Server Error**: A server or database connection error occurred.

### 10. Retrieve All Active Feature Toggles Within a Specific Date Range for a Package

**Endpoint**: `GET /feature-toggles/{package_name}/active-in-range`

**Description**: Retrieves all active feature toggles within a specific date range for a specified package.

#### Parameters

- **Path Parameters**:
  - `package_name` (string, required): The name of the package containing the features.

- **Query Parameters**:
  - `start_date` (string, required): The start date of the range in the format `YYYY-MM-DD`.
  - `end_date` (string, required): The end date of the range in the format `YYYY-MM-DD`.

#### Responses

- **200:** List of feature toggles.
  
  **Body** (JSON Array):

  ```json
  [
    {
      "name": "string",
      "description": "string",
      "beginning_date": "YYYY-MM-DD HH:MM:SS",
      "expiration_date": "YYYY-MM-DD HH:MM:SS",
      "created_at": "YYYY-MM-DD HH:MM:SS",
      "updated_at": "YYYY-MM-DD HH:MM:SS"
    }
  ]
  ```

- **404:** Package not found.
- **500:** Database connection error.

### 11. Retrieve Feature Usage Statistics for a Specific Package

**Endpoint**: `GET /feature-toggles/{package_name}/statistics`

**Description**: Retrieves usage statistics for feature toggles within a specified package.

#### Parameters

- **Path Parameters**:
  - `package_name` (string, required): The name of the package containing the features.

#### Responses

- **200 OK**: Successfully retrieved feature statistics.

  **Returned JSON**:

  ```json
  {
    "total_features": 10,
    "active_features": 5
  }
  ```

- **404:** Package not found.
- **500:** Database connection error.
