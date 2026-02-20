CREATE TABLE IF NOT EXISTS processed.dim_users (
    user_id             STRING NOT NULL,
    registered_date     DATE NOT NULL,
    age_group           STRING,
    membership_type     STRING
);