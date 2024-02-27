-- Wrting some random tests to make sure database works
INSERT INTO Quiz_Creator (creatorEmail, password, firstName, lastName) VALUES
('john.doe@example.com', 'password123', 'John', 'Doe');

INSERT INTO Quiz_Taker (takerEmail, firstName, lastName) VALUES
('jane.smith@example.com', 'Jane', 'Smith'),
('alex.brown@example.com', 'Alex', 'Brown');

INSERT INTO Quiz (creatorID, time) VALUES
(1, 30);

INSERT INTO Question (quizID, type, details, score) VALUES
(1, 'multiple-choice', 'What is the capital of France?', 10),
(1, 'true-false', 'The sky is blue.', 5);

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


-- TO TEST QUIZ TAKER PAGE
INSERT INTO Quiz (creatorID, time) VALUES
(1, 30);

INSERT INTO Question (quizID, type, details, score) VALUES
(10, 'multiple-choice', 'What is the capital of France?', 10),
(10, 'true-false', 'The light from the Sun reaches the Earth in about 8 minutes and 20 seconds.', 5),
(10, 'check-all', 'Which of the following are planets in our Solar System?', 10),
(10, 'multiple-choice', 'Who wrote the play "Romeo and Juliet"?', 10),
(10, 'true-false', 'Water boils at 100 degrees Celsius at sea level.', 5),
(10, 'check-all', 'Which of the following elements are noble gases?', 10),
(10, 'multiple-choice', 'What is the largest mammal in the world?', 10),
(10, 'true-false', 'Albert Einstein was awarded the Nobel Prize in Physics in 1921 for his discovery of the photoelectric effect.', 5),
(10, 'check-all', 'Which of the following are official languages in Switzerland?', 10),
(10, 'freeform', 'What is the name of the longest river in the world?', 15);

-- Answers for Q1 (Question ID 33)
INSERT INTO Answers (questionID, details, correct) VALUES
(33, 'Paris', TRUE),
(33, 'Madrid', FALSE),
(33, 'London', FALSE),
(33, 'Berlin', FALSE);

-- Answers for Q2 (Question ID 34)
INSERT INTO Answers (questionID, details, correct) VALUES
(34, 'True', TRUE),
(34, 'False', FALSE);

-- Answers for Q3 (Question ID 35)
INSERT INTO Answers (questionID, details, correct) VALUES
(35, 'Pluto', FALSE),
(35, 'Mars', TRUE),
(35, 'Venus', TRUE),
(35, 'Sirius', FALSE);

-- Answers for Q4 (Question ID 36)
INSERT INTO Answers (questionID, details, correct) VALUES
(36, 'Charles Dickens', FALSE),
(36, 'William Shakespeare', TRUE),
(36, 'Jane Austen', FALSE),
(36, 'Leo Tolstoy', FALSE);

-- Answers for Q5 (Question ID 37)
INSERT INTO Answers (questionID, details, correct) VALUES
(37, 'True', TRUE),
(37, 'False', FALSE);

-- Answers for Q6 (Question ID 38)
INSERT INTO Answers (questionID, details, correct) VALUES
(38, 'Helium', TRUE),
(38, 'Oxygen', FALSE),
(38, 'Argon', TRUE),
(38, 'Neon', TRUE);

-- Answers for Q7 (Question ID 39)
INSERT INTO Answers (questionID, details, correct) VALUES
(39, 'African Elephant', FALSE),
(39, 'Blue Whale', TRUE),
(39, 'Giraffe', FALSE),
(39, 'White Rhino', FALSE);

-- Answers for Q8 (Question ID 40)
INSERT INTO Answers (questionID, details, correct) VALUES
(40, 'True', TRUE),
(40, 'False', FALSE);

-- Answers for Q9 (Question ID 41)
INSERT INTO Answers (questionID, details, correct) VALUES
(41, 'French', TRUE),
(41, 'German', TRUE),
(41, 'English', FALSE),
(41, 'Italian', TRUE);

INSERT INTO Results (takerID, quizID, timeTaken, totalScore, completed) VALUES
(1, 10, 0, 0, FALSE);