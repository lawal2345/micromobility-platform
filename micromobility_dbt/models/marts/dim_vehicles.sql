with stg as (
    select * from {{ ref('stg_vehicle_telemetry') }}
),

latest as (
    select
        vehicle_id,
        vehicle_type,
        battery_level_pct   as current_battery_pct,
        event_type          as current_status,
        recorded_at         as last_seen_at,
        row_number() over (
            partition by vehicle_id
            order by recorded_at desc
        ) as rn
    from stg
)

select
    vehicle_id,
    vehicle_type,
    current_battery_pct,
    current_status,
    last_seen_at
from latest
where rn = 1