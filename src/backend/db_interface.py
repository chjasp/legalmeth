# DB connection
from google.cloud.sql.connector import Connector
from sqlalchemy import create_engine, text
from google.oauth2 import service_account
import google.auth

# Ensure the following is done at the beginning of your code or entry point of your application
credentials = service_account.Credentials.from_service_account_file(
    "./blue-pg-sa-creds.json",
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)

class DatabaseInterface:
    def __init__(self, instance_connection_name, db_user, db_pass, db_name):
        self.instance_connection_name = instance_connection_name
        self.db_user = db_user
        self.db_pass = db_pass
        self.db_name = db_name
        self.connector = Connector(credentials=credentials)
        self.pool = self.create_pool()

    def get_conn(self):

        conn = self.connector.connect(
            self.instance_connection_name,
            "pg8000",
            user=self.db_user,
            password=self.db_pass,
            db=self.db_name
        )
        return conn

    def create_pool(self):
        return create_engine(
            "postgresql+pg8000://",
            creator=self.get_conn,
        )
    
    def run_query(self, query, fetch=True):
        with self.pool.connect() as connection:
            try:
                result = connection.execute(text(query))
                connection.commit() 
                if fetch:
                    return result.fetchall()
                else:
                    return None
            except Exception as e:
                    print("EXCEPTION THROWN")
                    print(e)
                    connection.rollback()  
            
    def insert_data_from_dataframe(self, dataframe, table_name):
            try:
                dataframe.to_sql(
                    table_name,
                    self.pool,
                    if_exists='append',
                    index=False,
                    method='multi'
                )
            except Exception as e:
                print("EXCEPTION THROWN DURING INSERT")
                print(e)
        
    def create_table(self, table_name, columns):
        """
        Creates a table with the given name and columns.
        :param table_name: The name of the table
        :param columns: A dictionary where keys are column names and values are SQL data types
        """
        cols = ', '.join(f'{col} {dtype}' for col, dtype in columns.items())
        create_table_query = f'CREATE TABLE {table_name} ({cols});'
        self.run_query(create_table_query, fetch=False)

    def drop_table(self, table_name):
        """
        Drops the table with the given name.
        :param table_name: The name of the table
        """
        drop_table_query = f'DROP TABLE {table_name};'
        print(self.run_query(drop_table_query, fetch=False))