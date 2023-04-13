CREATE TABLE IF NOT EXISTS account (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    fullname varchar(50) NOT NULL,
    email varchar(50) NOT NULL,
    username varchar(25) UNIQUE NOT NULL,
    password varchar(70) NOT NULL
);

CREATE TYPE STATUS AS ENUM('Active', 'Inactive');

CREATE TABLE IF NOT EXISTS conversation (
    conversation_id INT GENERATED ALWAYS AS IDENTITY,
    account_id INT NOT NULL,
    status STATUS NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration INT,
    PRIMARY KEY (conversation_id),
    FOREIGN KEY (account_id)
        REFERENCES account (id)
        ON UPDATE RESTRICT 
        ON DELETE CASCADE
);

CREATE TYPE LEVEL AS ENUM('1', '2', '3', '4', '5','6');

CREATE TABLE IF NOT EXISTS grammar (
    grammar_id INT GENERATED ALWAYS AS IDENTITY,
    conversation_id INT NOT NULL,
    pattern varchar(75) NOT NULL,
    level LEVEL NOT NULL,
    PRIMARY KEY (grammar_id),
    FOREIGN KEY (conversation_id)
        REFERENCES conversation (conversation_id)
        ON UPDATE RESTRICT 
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS word (
    word_id INT GENERATED ALWAYS AS IDENTITY,
    conversation_id INT NOT NULL,
    word varchar(25) NOT NULL,
    level LEVEL NOT NULL,
    PRIMARY KEY (word_id),
    FOREIGN KEY (conversation_id)
        REFERENCES conversation (conversation_id)
        ON UPDATE RESTRICT 
        ON DELETE CASCADE
)

