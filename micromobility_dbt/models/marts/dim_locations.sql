with stg as (
    select * from {{ ref('stg_vehicle_telemetry') }}
),

locations as (
    select distinct
        cast(round(latitude, 4) as string) || '_' ||
        cast(round(longitude, 4) as string)     as location_id,
        round(latitude, 4)                      as latitude,
        round(longitude, 4)                     as longitude
    from stg
    where latitude is not null
      and longitude is not null
)

select * from locations