-- Disabling foreign key checks and turning off autocommit
SET FOREIGN_KEY_CHECKS = 0;
SET AUTOCOMMIT = 0;

-- Dropping all the tables, starting from the bottom up to avoid
-- any issues with foreign key constraints
DROP TABLE IF EXISTS Response;
DROP TABLE IF EXISTS Results;
DROP TABLE IF EXISTS Answers;
DROP TABLE IF EXISTS Question;
DROP TABLE IF EXISTS Quiz;
DROP TABLE IF EXISTS Quiz_Taker;
DROP TABLE IF EXISTS Quiz_Creator;

-- Table for Quiz Creator
CREATE OR REPLACE TABLE Quiz_Creator (
    creatorID INT AUTO_INCREMENT UNIQUE NOT NULL,
    creatorEmail VARCHAR(70) UNIQUE NOT NULL,
    password VARCHAR(1000) NOT NULL,
    firstName VARCHAR(50) NOT NULL,
    lastName VARCHAR(50) NOT NULL,
    PRIMARY KEY (creatorID)
);

-- Table for Quiz Taker
CREATE OR REPLACE TABLE Quiz_Taker (
    takerID INT AUTO_INCREMENT UNIQUE NOT NULL,
    takerEmail VARCHAR(70) UNIQUE NOT NULL,
    firstName VARCHAR(50),
    lastName VARCHAR(50),
    PRIMARY KEY (takerID)
);

-- Table for Quiz
CREATE OR REPLACE TABLE Quiz (
    quizID INT AUTO_INCREMENT UNIQUE NOT NULL,
    creatorID INT NOT NULL,
    time INT NOT NULL,
    PRIMARY KEY (quizID),
    FOREIGN KEY (creatorID) REFERENCES Quiz_Creator(creatorID)
);

-- Table for Question
CREATE OR REPLACE TABLE Question (
    questionID INT AUTO_INCREMENT UNIQUE NOT NULL,
    quizID INT NOT NULL,
    type VARCHAR(255) NOT NULL,
    details VARCHAR(500) NOT NULL,
    score INT NOT NULL,
    PRIMARY KEY (questionID),
    FOREIGN KEY (quizID) REFERENCES Quiz(quizID)
);

-- Table for Answers
CREATE OR REPLACE TABLE Answers (
    answerID INT AUTO_INCREMENT UNIQUE NOT NULL,
    questionID INT NOT NULL,
    details VARCHAR(500) NOT NULL,
    correct BOOLEAN,
    PRIMARY KEY (answerID),
    FOREIGN KEY (questionID) REFERENCES Question(questionID)
);

-- Table for Results
CREATE OR REPLACE TABLE Results (
    linkID INT AUTO_INCREMENT UNIQUE NOT NULL,
    takerID INT NOT NULL,
    quizID INT NOT NULL,
    timeTaken INT NOT NULL,
    totalScore DECIMAL(5, 2),
    completed BOOLEAN DEFAULT False,
    PRIMARY KEY (linkID),
    FOREIGN KEY (takerID) REFERENCES Quiz_Taker(takerID),
    FOREIGN KEY (quizID) REFERENCES Quiz(quizID)
);

-- Table for Response
CREATE OR REPLACE TABLE Response (
    responseID INT AUTO_INCREMENT UNIQUE NOT NULL,
    linkID INT NOT NULL,
    questionID INT NOT NULL,
    response VARCHAR(255),
    PRIMARY KEY (responseID),
    FOREIGN KEY (linkID) REFERENCES Results(linkID),
    FOREIGN KEY (questionID) REFERENCES Question(questionID)
);

SET FOREIGN_KEY_CHECKS = 1;
COMMIT;
