CREATE TABLE IF NOT EXISTS users
(
    id SERIAL PRIMARY KEY,
    token character varying(255) NOT NULL,
    tg_id integer,
    tg_name text,
    tg_surname text,
    vk_id integer,
    vk_name text,
    vk_surname text
);