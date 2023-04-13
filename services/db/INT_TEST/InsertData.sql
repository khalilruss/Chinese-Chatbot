INSERT INTO account (fullname, email, username, password) 
VALUES ('Test User', 'test@mail.com','test','$2b$12$91FYyuXMLR6YchxNo03T9O/4Zao97pMakx8c39jmnANNlPbSnGzwG');

INSERT INTO conversation (account_id, status, start_time) 
VALUES (1, 'Active', '2021-03-26 22:21:53.728529');

INSERT INTO grammar (conversation_id, pattern, level) 
VALUES (1,'没 (+ Obj.)','1');

INSERT INTO word (conversation_id, word, level) 
VALUES (1,'什么','1');