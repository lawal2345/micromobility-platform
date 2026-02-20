with stg as (
    select * from {{ ref('stg_vehicle_telemetry') }}
    where trip_id is not null
),

trips as (
    select
        trip_id,
        vehicle_id,
        min(recorded_at)                                as trip_start_at,
        max(recorded_at)                                as trip_end_at,
        timestamp_diff(
            max(recorded_at), min(recorded_at), minute
        )                                               as duration_minutes,
        round(avg(speed_kmh), 2)                        as avg_speed_kmh,
        round(max(speed_kmh), 2)                        as max_speed_kmh,
        max(battery_level_pct) - min(battery_level_pct) as battery_consumed_pct,
        date(min(recorded_at))                          as trip_date
    from stg
    group by trip_id, vehicle_id
)

select * from trips