from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os


# Load the environment variables
load_dotenv()

print("mongo db file")
# Construct the MongoDB URI
DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING")
DB_NAME = os.getenv("DB_NAME")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
print(f"Raw DB_PASSWORD: '{DB_PASSWORD}'")  
print(os.getenv("GG"))

MONGO_URI = f"mongodb+srv://{DB_USERNAME}:{DB_PASSWORD}@{DB_CONNECTION_STRING}/{DB_NAME}"

class MongoConnectionHolder:
    __db = None

    @staticmethod
    def initialize_db():
        """
        Initialize the database connection

        :return: MongoDB connection
         :rtype: Database
        """
        if MongoConnectionHolder.__db is None:
            try:
                print("Initializing MongoDB connection...")
                # Create a new client and connect to the server
                client = MongoClient(MONGO_URI, server_api=ServerApi('1'))

                # Send a ping to confirm a successful connection
                client.admin.command('ping')
                print("Pinged your deployment. You successfully connected to MongoDB!")
                
                MongoConnectionHolder.__db = client[DB_NAME]
            except Exception as e:
                print(e)
        return MongoConnectionHolder.__db

    @staticmethod
    def get_db():
        """
        Get the database connection

        :return: MongoDB connection
        :rtype: Database
        """
        if MongoConnectionHolder.__db is None:
            MongoConnectionHolder.initialize_db()

        return MongoConnectionHolder.__db
