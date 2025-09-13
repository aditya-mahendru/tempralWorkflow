CREATE TABLE orders (
    id UUID PRIMARY KEY,
    order_data jsonb NOT NULL,
    address_json jsonb NOT NULL,
    order_status VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NULL DEFAULT NOW()
);

CREATE TABLE payments (
    id UUID PRIMARY KEY,
    order_id UUID NOT NULL,
    payment_status int4 NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE events(
    id int4 PRIMARY KEY AUTOINCREMENT,
    order_id UUID NOT NULL,
    type text NOT NULL,
    payload jsonb NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
)