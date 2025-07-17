import duckdb
import pandas as pd
import asyncio
import numpy as np
from datetime import datetime, timedelta, time, date
from app.utils.general import load_config

SAMPLE_FRAC    = 0.30
DAYS_AHEAD     = 28
OPEN_TIME      = time(8, 0)
CLOSE_TIME     = time(20, 0)
SLOT_MINUTES   = 30
BOOKED_RATIO   = 0.30

def main():
    config = asyncio.run(load_config("config/config.yml"))
    con = duckdb.connect(config["database"])

    df = (
        con.execute("SELECT * FROM propriedades")
        .fetchdf()
        .sample(frac=SAMPLE_FRAC, random_state=42)
        .drop_duplicates(subset="id")
        .reset_index(drop=True)
        .rename(columns={"id": "property_id"})
    )

    PROPERTY_COLUMNS = [
        "property_id", "preco", "tamanho", "n_quartos", "n_banheiros",
        "n_garagem", "rua", "bairro", "cidade", "latitude", "longitude"
    ]

    con.execute("""
    CREATE TABLE IF NOT EXISTS properties (
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
    CREATE TABLE IF NOT EXISTS property_slots (
        property_id VARCHAR,
        slot_start  TIMESTAMP WITH TIME ZONE,
        slot_end    TIMESTAMP WITH TIME ZONE,
        status      VARCHAR,
        CONSTRAINT pk PRIMARY KEY (property_id, slot_start),
        CONSTRAINT fk_prop FOREIGN KEY (property_id)
            REFERENCES properties(property_id)
    );
    """)

    con.execute("DELETE FROM properties;")
    con.register("tmp_props", df[PROPERTY_COLUMNS])
    con.execute("INSERT INTO properties SELECT * FROM tmp_props;")
    con.unregister("tmp_props")

    now = datetime.now().astimezone()
    to_next = (SLOT_MINUTES - now.minute % SLOT_MINUTES) % SLOT_MINUTES
    start_dt = (now + timedelta(minutes=to_next)).replace(second=0, microsecond=0)

    all_slots = []
    for d in range(DAYS_AHEAD):
        day: date = (start_dt + timedelta(days=d)).date()
        if day.weekday() == 6:
            continue
        t = datetime.combine(day, OPEN_TIME, tzinfo=start_dt.tzinfo)
        while t.time() < CLOSE_TIME:
            all_slots.append(t)
            t += timedelta(minutes=SLOT_MINUTES)

    slots_df = (
        pd.MultiIndex.from_product([df["property_id"], all_slots],
                                   names=["property_id", "slot_start"])
        .to_frame(index=False)
    )
    slots_df["slot_end"] = slots_df["slot_start"] + timedelta(minutes=SLOT_MINUTES)

    rng = np.random.default_rng(seed=42)
    mask = rng.random(len(slots_df)) < BOOKED_RATIO
    slots_df["status"] = np.where(mask, "booked", "free")

    con.execute("DELETE FROM property_slots;")
    con.register("tmp_slots", slots_df)
    con.execute("INSERT INTO property_slots SELECT * FROM tmp_slots;")
    con.unregister("tmp_slots")

    total  = len(slots_df)
    booked = mask.sum()
    print(f"{total:,} slots inserted ({booked:,} booked, {total-booked:,} free)")

    con.close()

if __name__ == "__main__":
    main()
