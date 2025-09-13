import psycopg2
from temporalio import workflow
from dotenv import load_dotenv
# from loguru import logger
import os

load_dotenv()

class PostgresDB:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.connect()
    
    def connect(self):
        try:
            self.conn = psycopg2.connect(
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT"),
                database=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD")
            )
            self.cursor = self.conn.cursor()
            workflow.logger.info("Connected to PostgreSQL")
        except Exception as e:
            workflow.logger.error(f"Error connecting to PostgreSQL: {e}")
            raise e
        
    async def query_executor(self, query, hasReturn:bool=True):
        try:
            self.cursor.execute(query)
            self.conn.commit()
            
            if hasReturn:
                return self.cursor.fetchall()
            else:
                return
        except Exception as e:
            workflow.logger.error(f"Error executing query: {e}")
            raise e
    
    def __del__(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()