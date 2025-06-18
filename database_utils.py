import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
def use_db(
    dbname,
    user,
    password,
    host="localhost",
    port="5432",
    autocommit=False,
    callback=None
):
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        if autocommit:
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        cursor = conn.cursor()
        if callback:
            callback(cursor, conn)
        if not autocommit:
            conn.commit()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def save_company_to_db(cursor, company):
    # Check if company_id is None - this is required for the primary key
    if company.company_id is None:
        print(f"Skipping company with None ID: {getattr(company, 'brand', 'Unknown brand')}")
        return
    
    cursor.execute("SELECT 1 FROM companies WHERE id = %s;", (company.company_id,))
    exists = cursor.fetchone()

    if exists:
        print(f"Duplicate ID skipped: {company.company_id} - {getattr(company, 'brand', 'Unknown brand')}")
    else:
        # Handle None values for address fields
        address = getattr(company, 'address', None)
        city = getattr(company, 'city', None)
        state = getattr(company, 'state', None)
        postal_code = getattr(company, 'postalCode', None)
        
        # Check if address is None - required field
        if address is None:
            print(f"Skipping company {company.company_id} - {getattr(company, 'brand', 'Unknown brand')}: missing required address")
            return
        
        # Insert address or get existing one
        cursor.execute("""
            INSERT INTO addresses (address, city, state, postalcode)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (address, city, state, postalcode) 
            DO UPDATE SET address = EXCLUDED.address
            RETURNING id;
        """, (address, city, state, postal_code))
        
        address_id = cursor.fetchone()[0]

        # Handle None values for company fields
        brand = getattr(company, 'brand', None)
        phone = getattr(company, 'phone', None)
        
        cursor.execute("""
            INSERT INTO companies (id, brand, phone, address_id)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING;
        """, (
            company.company_id,
            brand,
            phone,
            address_id
        ))