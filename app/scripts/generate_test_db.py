import duckdb
import pandas as pd
from datetime import datetime, timedelta

def main():
    """
    This script generates a dedicated test database (test_db.db)
    with specific data required for the tests in tests.py to pass.
    """
    db_path = "tests/test_db.db"
    con = duckdb.connect(db_path)

    print(f"Creating test database at {db_path}...")

    # --- Create Schemas ---
    con.execute("""
    CREATE OR REPLACE TABLE properties (
        property_id    VARCHAR PRIMARY KEY,
        preco          DOUBLE,
        tamanho        DOUBLE,
        n_quartos      INTEGER,
        n_banheiros    INTEGER,
        n_garagem      INTEGER,
        rua            VARCHAR,
        bairro         VARCHAR,
        cidade         VARCHAR,
        latitude       DOUBLE,
        longitude      DOUBLE
    );
    """)

    con.execute("""
    CREATE OR REPLACE TABLE property_slots (
        property_id VARCHAR,
        slot_start  TIMESTAMP,
        slot_end    TIMESTAMP,
        status      VARCHAR,
        CONSTRAINT pk PRIMARY KEY (property_id, slot_start)
    );
    """)

    # --- Properties Data ---
    properties_data = [
        # Property for successful search test in Curitiba
        ('curitiba_1', 550000.0, 120.0, 2, 2, 1, 'Rua das Flores', 'Centro', 'Curitiba', -25.4284, -49.2733),
        
        # Your test property for booking a FREE slot
        ('abcfoo42', 750000.0, 150.0, 3, 2, 2, 'Avenida Principal', 'Batel', 'Curitiba', -25.4411, -49.2931),

        # A separate property for cancelling a BOOKED slot
        ('xyzbar99', 850000.0, 180.0, 4, 3, 2, 'Rua da Praia', 'Beira Mar', 'Florianopolis', -27.5954, -48.5480),
    ]
    properties_df = pd.DataFrame(properties_data, columns=['property_id', 'preco', 'tamanho', 'n_quartos', 'n_banheiros', 'n_garagem', 'rua', 'bairro', 'cidade', 'latitude', 'longitude'])
    
    # --- Slots Data ---
    slots_data = [
        # Available FREE slot for booking test on property 'abcfoo42'
        ('abcfoo42', datetime(2024, 12, 25, 10, 0, 0), datetime(2024, 12, 25, 10, 30, 0), 'free'),
        ('abcfoo42', datetime(2024, 12, 25, 11, 0, 0), datetime(2024, 12, 25, 11, 30, 0), 'free'),
        
        # Already BOOKED slot for cancellation test on property 'xyzbar99'
        ('xyzbar99', datetime(2024, 12, 25, 10, 0, 0), datetime(2024, 12, 25, 10, 30, 0), 'booked'),
    ]
    slots_df = pd.DataFrame(slots_data, columns=['property_id', 'slot_start', 'slot_end', 'status'])

    # --- Insert Data ---
    con.register('properties_df', properties_df)
    con.execute('INSERT INTO properties SELECT * FROM properties_df')
    
    con.register('slots_df', slots_df)
    con.execute('INSERT INTO property_slots SELECT * FROM slots_df')

    print("Test properties inserted:")
    con.table('properties').show()

    print("Test slots inserted:")
    con.table('property_slots').show()

    con.close()
    print("Test database created successfully.")

if __name__ == "__main__":
    main() 