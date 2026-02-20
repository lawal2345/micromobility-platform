with stg as (
    select * from {{ ref('stg_vehicle_telemetry') }}
),

dates as (
    select distinct
        date(recorded_at)                           as date_id,
        extract(year  from recorded_at)             as year,
        extract(month from recorded_at)             as month,
        extract(day   from recorded_at)             as day,
        extract(dayofweek from recorded_at)         as day_of_week,
        extract(hour  from recorded_at)             as hour
    from stg
)

select * from dates