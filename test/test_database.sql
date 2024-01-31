-- Wrting some random tests to make sure database works
INSERT INTO Quiz_Creator (creatorEmail, password, firstName, lastName) VALUES
('john.doe@example.com', 'password123', 'John', 'Doe');

INSERT INTO Quiz_Taker (takerEmail, firstName, lastName) VALUES
('jane.smith@example.com', 'Jane', 'Smith'),
('alex.brown@example.com', 'Alex', 'Brown');

INSERT INTO Quiz (creatorID, time) VALUES
(1, 30);

INSERT INTO Question (quizID, type, details, score) VALUES
(1, 'Multiple Choice', 'What is the capital of France?', 10),
(1, 'True/False', 'The sky is blue.', 5);

INSERT INTO Answers (questionID, details, correct) VALUES
(1, 'Paris', TRUE),
(1, 'London', FALSE),
(1, 'Berlin', FALSE),
(2, 'True', TRUE),
(2, 'False', FALSE);

INSERT INTO Results (takerID, quizID, timeTaken, totalScore, completed) VALUES
(1, 1, 15, 15, TRUE);

INSERT INTO Response (linkID, questionID, response) VALUES
(1, 1, 'Paris'),
(1, 2, 'True');


-- After finishing testing, you can uncomment the queries below to clear out the database:
-- Dropping the tables in reverse order to avoid foreign key constraint issues
-- DROP TABLE IF EXISTS Response;
-- DROP TABLE IF EXISTS Results;
-- DROP TABLE IF EXISTS Answers;
-- DROP TABLE IF EXISTS Question;
-- DROP TABLE IF EXISTS Quiz;
-- DROP TABLE IF EXISTS Quiz_Taker;
-- DROP TABLE IF EXISTS Quiz_Creator;
