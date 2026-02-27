CREATE TABLE
    IF NOT EXISTS products (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
        name TEXT NOT NULL,
        description TEXT,
        price NUMERIC(10, 2) NOT NULL, -- 10 casas, 2 decimais
        quantity_in_stock INTEGER NOT NULL DEFAULT 0,
        creation_time TIMESTAMP DEFAULT NOW ()
    );

CREATE TABLE
    IF NOT EXISTS orders (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
        buyer_id TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT NOW ()
    );

CREATE TABLE
    IF NOT EXISTS order_items (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
        order_id UUID REFERENCES orders (id),
        product_id UUID REFERENCES products (id),
        quantity INTEGER NOT NULL
    );

INSERT INTO
    products (name, description, price, quantity_in_stock)
VALUES
    ('Notebook', 'Notebook 15 polegadas', 3500.00, 10),
    ('Mouse', 'Mouse sem fio', 150.00, 50),
    ('Teclado', 'Teclado mecânico', 400.00, 30) ON CONFLICT DO NOTHING;