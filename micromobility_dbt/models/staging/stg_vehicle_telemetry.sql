with source as (
    select * from {{ source('raw', 'raw_telemetry') }}
),

cleaned as (
    select
        cast(event_id       as string)      as event_id,
        cast(vehicle_id     as string)      as vehicle_id,
        cast(trip_id         as string)      as trip_id,
        cast(timestamp       as timestamp)   as recorded_at,
        cast(latitude        as float64)     as latitude,
        cast(longitude       as float64)     as longitude,
        cast(speed_kmh      as float64)     as speed_kmh,
        cast(battery_level  as int64)       as battery_level_pct,
        lower(trim(cast(event_type as string))) as event_type,
        lower(trim(cast(vehicle_type as string))) as vehicle_type
    from source

    where vehicle_id is not null
        and timestamp is not null

)

select * from cleaned