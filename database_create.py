import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import psycopg2.errors
from database_utils import use_db
DB_NAME = "bbb"
DB_USERNAME = "postgres"
DB_PASSWORD = "1234"


def create_database(cursor, _):
    try:
        cursor.execute(f"CREATE DATABASE {DB_NAME}")
        print(f"Database '{DB_NAME}' created successfully.")
    except psycopg2.errors.DuplicateDatabase:
        print(f"Database '{DB_NAME}' already exists.")


def create_tables(cursor, _):

    try:
        cursor.execute("""
        CREATE TABLE addresses (
            id SERIAL PRIMARY KEY,
            address TEXT NOT NULL,
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            postalcode TEXT NOT NULL,
            UNIQUE (address, city, state, postalcode)
        );
        """)
        print("Table 'addresses' created.")
    except psycopg2.errors.DuplicateTable:
        print("Table 'addresses' already exists.")


    try:
        cursor.execute("""
        CREATE TABLE companies (
            id VARCHAR PRIMARY KEY,
            brand VARCHAR,
            phone TEXT[],
            address_id INTEGER UNIQUE,
            owner VARCHAR,
            CONSTRAINT fk_address FOREIGN KEY (address_id)
                REFERENCES addresses(id)
                ON DELETE SET NULL
        );
        """)
        print("Table 'companies' created.")
    except psycopg2.errors.DuplicateTable:
        print("Table 'companies' already exists.")


# Create database
use_db(
    dbname="postgres",
    user=DB_USERNAME,
    password=DB_PASSWORD,
    autocommit=True,
    callback=create_database
)

# Create tables
use_db(
    dbname=DB_NAME,
    user=DB_USERNAME,
    password=DB_PASSWORD,
    callback=create_tables
)



