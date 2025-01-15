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

## POST /feature-toggle

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

**Responses:**
- **201:** Feature toggle created successfully.
- **400:** Invalid request or date format.
- **500:** Database connection error.

---

### 2. Get All Features for a Package
**GET /feature-toggles/{package_name}**

**Description**: Retrieves all feature toggles for the specified package.

#### Parameters:
- **Path Parameters**:
  - `package_name` (string, required): The name of the package.

#### Responses:
- **200**: Successfully retrieved feature toggles.
  - **Body** (JSON Array):
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

 
 ### 3. Get All Active Feature Toggles for a Package by Date

**Endpoint**: `GET /feature-toggles/{package_name}/by-date`

**Description**:  
Retrieves all active feature toggles for a specific package on a given date. A feature toggle is considered active if the specified date falls within its `beginning_date` and `expiration_date`.

---

#### Parameters:

- **Path Parameters**:
  - `package_name` (string, required): The name of the package.

- **Query Parameters**:
  - `date` (string, required): The specific date in the format `YYYY-MM-DD`.

---

#### Responses:

- **200 OK**: Successfully retrieved active feature toggles for the specified date.
  - **Body** (JSON Array):
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
  - **Body**:
    ```json
    {
      "error": "Invalid date format, use YYYY-MM-DD"
    }
    ```

- **404 Not Found**: The specified package does not exist.
  - **Body**:
    ```json
    {
      "error": "Package 'example_package' does not exist"
    }
    ```

- **500 Internal Server Error**: A server or database connection error occurred.
  - **Body**:
    ```json
    {
      "error": "Database not initialized"
    }
    ```
    
    ### 4. Delete All Feature Toggles for a Package

**Endpoint**: `DELETE /feature-toggles/{package_name}`

**Description**:  
Deletes all feature toggles for the specified package.

---

#### Parameters:

- **Path Parameters**:
  - `package_name` (string, required): The name of the package whose feature toggles will be deleted.

---

#### Responses:

- **200 OK**: Successfully deleted all feature toggles for the specified package.
  - **Body**:
    ```json
    {
      "message": "All feature toggles deleted"
    }
    ```

- **404 Not Found**: The specified package does not exist.
  - **Body**:
    ```json
    {
      "error": "Package 'example_package' does not exist"
    }
    ```

- **500 Internal Server Error**: A server or database connection error occurred.
  - **Body**:
    ```json
    {
      "error": "Could not connect to the database"
    }
    ```

---




---





