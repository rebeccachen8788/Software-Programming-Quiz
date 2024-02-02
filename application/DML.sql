-- Insert a new Quiz Creator
INSERT INTO Quiz_Creator (creatorEmail, password, firstName, lastName)
VALUES ({{creatorEmail}}, {{password}}, {{firstName}}, {{lastName}});

-- Select Quiz Creators with their names
SELECT creatorID, CONCAT(firstName, ' ', lastName) AS creatorName
FROM Quiz_Creator;

-- Update Quiz Creator information
UPDATE Quiz_Creator
SET creatorEmail = {{newCreatorEmail}}, password = {{newPassword}}, firstName = {{newFirstName}}, lastName = {{newLastName}}
WHERE creatorID = {{creatorID}};

-- Insert a new Quiz Taker
INSERT INTO Quiz_Taker (takerEmail, firstName, lastName)
VALUES ({{takerEmail}}, {{firstName}}, {{lastName}});

-- Select Quiz Takers with their names
SELECT takerID, CONCAT(firstName, ' ', lastName) AS takerName
FROM Quiz_Taker;

-- Update Quiz Taker information
UPDATE Quiz_Taker
SET takerEmail = {{newTakerEmail}}, firstName = {{newFirstName}}, lastName = {{newLastName}}
WHERE takerID = {{takerID}};

-- Insert a new Quiz
INSERT INTO Quiz (creatorID, time)
VALUES ({{creatorID}}, {{time}});

-- Select Quizzes with their details
SELECT quizID, creatorID, time
FROM Quiz;

-- Update Quiz information
UPDATE Quiz
SET creatorID = {{newCreatorID}}, time = {{newTime}}
WHERE quizID = {{quizID}};

-- Insert a new Question
INSERT INTO Question (quizID, type, details, score)
VALUES ({{quizID}}, {{type}}, {{details}}, {{score}});

-- Select Questions with their details
SELECT questionID, quizID, type, details, score
FROM Question;

-- Update Question information
UPDATE Question
SET quizID = {{newQuizID}}, type = {{newType}}, details = {{newDetails}}, score = {{newScore}}
WHERE questionID = {{questionID}};

-- Insert Answers for a Question
INSERT INTO Answers (questionID, details, correct)
VALUES ({{questionID}}, {{details}}, {{correct}});

-- Select Answers with their details
SELECT answerID, questionID, details, correct
FROM Answers;

-- Update Answer information
UPDATE Answers
SET questionID = {{newQuestionID}}, details = {{newDetails}}, correct = {{newCorrect}}
WHERE answerID = {{answerID}};

-- Insert Results for a Quiz taken by a Taker
INSERT INTO Results (takerID, quizID, timeTaken, totalScore, completed)
VALUES ({{takerID}}, {{quizID}}, {{timeTaken}}, {{totalScore}}, {{completed}});

-- Select Results with their details
SELECT linkID, takerID, quizID, timeTaken, totalScore, completed
FROM Results;

-- Update Results information
UPDATE Results
SET takerID = {{newTakerID}}, quizID = {{newQuizID}}, timeTaken = {{newTimeTaken}}, totalScore = {{newTotalScore}}, completed = {{newCompleted}}
WHERE linkID = {{linkID}};

-- Insert a Response for a Question in a Result
INSERT INTO Response (linkID, questionID, response)
VALUES ({{linkID}}, {{questionID}}, {{response}});

-- Select Responses with their details
SELECT responseID, linkID, questionID, response
FROM Response;

-- Update Response information
UPDATE Response
SET linkID = {{newLinkID}}, questionID = {{newQuestionID}}, response = {{newResponse}}
WHERE responseID = {{responseID}};
