drop TABLE if EXISTS weather_measures;
DROP TABLE if EXISTS geo_table;


CREATE TABLE IF NOT EXISTS geo_table (
    id serial primary key,
    city VARCHAR(50),
    country varchar(50),
    timezone varchar(50),
    latitude float,
    longitude float,

    constraint unq_loc unique(latitude, longitude)
);


CREATE TABLE IF NOT EXISTS weather_measures (
    id serial primary key,
    geo_id int not null,
    temperature float not null,
    humidity float,
    feels_like float,
    is_day boolean,
    precipitation float,
    cloud_cover float,
    wind_speed float,
    weather_code varchar(50),
    updated_at  timestamp,

    foreign key(geo_id) references geo_table(id),
    constraint unq_loc_time unique(geo_id, updated_at)
);


