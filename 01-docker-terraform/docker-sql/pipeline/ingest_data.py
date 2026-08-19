#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import click
from sqlalchemy import create_engine
from tqdm.auto import tqdm


dtype = {
    "VendorID": pd.Int64Dtype(),
    "passenger_count": pd.Int64Dtype(),
    "trip_distance": pd.Float64Dtype(),
    "RatecodeID": pd.Int64Dtype(),
    "store_and_fwd_flag": pd.StringDtype(),
    "PULocationID": pd.Int64Dtype(),
    "DOLocationID": pd.Int64Dtype(),
    "payment_type": pd.Int64Dtype(),
    "trip_type": pd.Int64Dtype(),
    "fare_amount": pd.Float64Dtype(),
    "extra": pd.Float64Dtype(),
    "mta_tax": pd.Float64Dtype(),
    "tip_amount": pd.Float64Dtype(),
    "tolls_amount": pd.Float64Dtype(),
    "ehail_fee": pd.Float64Dtype(),
    "improvement_surcharge": pd.Float64Dtype(),
    "total_amount": pd.Float64Dtype(),
    "congestion_surcharge": pd.Float64Dtype(),
}

parse_dates = [
    "lpep_pickup_datetime",
    "lpep_dropoff_datetime",
]


@click.command()
@click.option('--pg-user', default='postgres', help='PostgreSQL user')
@click.option('--pg-pass', default='postgres', help='PostgreSQL password')
@click.option('--pg-host', default='db', help='PostgreSQL host')
@click.option('--pg-port', default=5433, type=int, help='PostgreSQL port')
@click.option('--pg-db', default='ny_taxi', help='PostgreSQL database name')
@click.option('--year', default=2021, type=int, help='Year of the data')
@click.option('--month', default=1, type=int, help='Month of the data')
@click.option('--target-table', default='green_taxi_data', help='Target table name')
@click.option('--chunksize', default=100000, type=int, help='Chunk size for inserting rows into Postgres')
def run(pg_user, pg_pass, pg_host, pg_port, pg_db, year, month, target_table, chunksize):
    """Ingest a parquet NYC taxi dataset into PostgreSQL."""
    prefix = 'https://d37ci6vzurychx.cloudfront.net/trip-data'
    url = f'{prefix}/green_tripdata_{year}-{month:02d}.parquet'

    engine = create_engine(
        f'postgresql+psycopg://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}'
    )

    df = pd.read_parquet(url)

    for column in dtype:
        if column in df.columns:
            df[column] = df[column].astype(dtype[column])

    for column in parse_dates:
        if column in df.columns:
            df[column] = pd.to_datetime(df[column])

    df.head(0).to_sql(
        name=target_table,
        con=engine,
        if_exists='replace',
        index=False,
    )

    for start in tqdm(range(0, len(df), chunksize), desc='Inserting rows'):
        chunk = df.iloc[start:start + chunksize].copy()
        chunk.to_sql(
            name=target_table,
            con=engine,
            if_exists='append',
            index=False,
        )

    url = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv"
    zone_df = pd.read_csv(url)

    zone_df.to_sql(
        name="zones",
        con=engine,
        if_exists='replace',
        index=False,
    )


if __name__ == '__main__':
    run()
