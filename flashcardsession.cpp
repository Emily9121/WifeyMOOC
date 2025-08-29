// flashcardsession.cpp
// The logic for our magical Leitner boxes and detailed progress saving!
#include "flashcardsession.h"
#include <QFileInfo>
#include <QDebug>
#include <algorithm>
#include <random>
#include <QRandomGenerator>

// The intervals for our magical Leitner boxes (in days)
const QMap<int, int> leitnerIntervals = {
    {1, 1}, {2, 3}, {3, 7}, {4, 14}, {5, 30}
};
const int MAX_BOX = 5;

FlashcardSession::FlashcardSession(const QList<Flashcard>& allCards, const QString& parleyFilePath, QObject *parent)
    : QObject(parent), allCards(allCards) {
    QFileInfo fileInfo(parleyFilePath);
    progressFilePath = fileInfo.absolutePath() + "/" + fileInfo.baseName() + ".progress.json";
    loadProgress();
}

void FlashcardSession::loadProgress() {
    QFile progressFile(progressFilePath);
    if (progressFile.open(QIODevice::ReadOnly)) {
        QJsonDocument doc = QJsonDocument::fromJson(progressFile.readAll());
        QJsonArray array = doc.array();
        for (const QJsonValue& value : array) {
            QJsonObject obj = value.toObject();
            FlashcardProgress p;
            p.cardId = obj["id"].toString();
            p.frontText = obj["front"].toString(); // Load front text
            p.backText = obj["back"].toString();   // Load back text
            p.box = obj["box"].toInt();
            p.nextReviewDate = QDateTime::fromString(obj["reviewDate"].toString(), Qt::ISODate);
            
            // --- ✨ Load the history of every attempt! ✨ ---
            QJsonArray attemptsArray = obj["attempts"].toArray();
            for (const QJsonValue& attemptVal : attemptsArray) {
                QJsonObject attemptObj = attemptVal.toObject();
                AttemptRecord attempt;
                attempt.date = QDateTime::fromString(attemptObj["date"].toString(), Qt::ISODate);
                attempt.wasCorrect = attemptObj["correct"].toBool();
                p.attempts.append(attempt);
            }
            progressMap[p.cardId] = p;
        }
    }

    // Make sure every card has a progress entry
    for (const auto& card : allCards) {
        if (!progressMap.contains(card.id)) {
            FlashcardProgress p;
            p.cardId = card.id;
            p.frontText = card.front; // Set initial text
            p.backText = card.back;   // Set initial text
            p.box = 1;
            p.nextReviewDate = QDateTime::currentDateTime().addDays(-1); // Ready for review now!
            progressMap[card.id] = p;
        }
    }
}

void FlashcardSession::saveProgress() {
    QJsonArray array;
    for (const auto& p : progressMap.values()) {
        QJsonObject obj;
        obj["id"] = p.cardId;
        obj["front"] = p.frontText; // Save front text
        obj["back"] = p.backText;   // Save back text
        obj["box"] = p.box;
        obj["reviewDate"] = p.nextReviewDate.toString(Qt::ISODate);

        // --- ✨ Save the full history of every attempt! ✨ ---
        QJsonArray attemptsArray;
        for (const auto& attempt : p.attempts) {
            QJsonObject attemptObj;
            attemptObj["date"] = attempt.date.toString(Qt::ISODate);
            attemptObj["correct"] = attempt.wasCorrect;
            attemptsArray.append(attemptObj);
        }
        obj["attempts"] = attemptsArray;
        
        array.append(obj);
    }
    QJsonDocument doc(array);
    QFile progressFile(progressFilePath);
    if (progressFile.open(QIODevice::WriteOnly)) {
        progressFile.write(doc.toJson());
    }
}

void FlashcardSession::startSession(int sessionSize) {
    sessionQueue.clear();
    QList<Flashcard> priorityQueue;
    QList<Flashcard> randomQueue;
    QDateTime now = QDateTime::currentDateTime();

    for (const auto& card : allCards) {
        if (progressMap[card.id].nextReviewDate <= now) {
            if (progressMap[card.id].box == 1) {
                priorityQueue.append(card);
            } else {
                randomQueue.append(card);
            }
        }
    }
    
    // Sort the priority cards by the number of past failures
    std::sort(priorityQueue.begin(), priorityQueue.end(), [&](const Flashcard& a, const Flashcard& b) {
        // Count failures for each card
        int failuresA = 0;
        for(const auto& attempt : progressMap[a.id].attempts) if(!attempt.wasCorrect) failuresA++;
        int failuresB = 0;
        for(const auto& attempt : progressMap[b.id].attempts) if(!attempt.wasCorrect) failuresB++;
        
        return failuresA > failuresB;
    });

    std::shuffle(randomQueue.begin(), randomQueue.end(), std::mt19937(QRandomGenerator::global()->generate()));

    sessionQueue = priorityQueue;
    sessionQueue.append(randomQueue);
    
    if (sessionQueue.size() > sessionSize) {
        sessionQueue = sessionQueue.mid(0, sessionSize);
    }
    
    originalSessionQueue = sessionQueue;
}

const Flashcard* FlashcardSession::getNextCard() {
    if (sessionQueue.isEmpty()) {
        if(currentCard) {
            delete currentCard;
            currentCard = nullptr;
        }
        saveProgress();
        return nullptr;
    }
    if(currentCard) delete currentCard;
    currentCard = new Flashcard(sessionQueue.takeFirst());
    return currentCard;
}

void FlashcardSession::recordAnswer(bool wasCorrect) {
    if (!currentCard) return;

    FlashcardProgress& p = progressMap[currentCard->id];

    // --- ✨ Record the attempt before we change anything! ✨ ---
    AttemptRecord newAttempt;
    newAttempt.date = QDateTime::currentDateTime();
    newAttempt.wasCorrect = wasCorrect;
    p.attempts.append(newAttempt);

    if (wasCorrect) {
        p.box = std::min(p.box + 1, MAX_BOX);
    } else {
        p.box = 1; 
    }
    p.nextReviewDate = QDateTime::currentDateTime().addDays(leitnerIntervals[p.box]);
}

int FlashcardSession::cardsRemaining() const {
    return sessionQueue.size();
}

int FlashcardSession::totalSessionCards() const {
    return originalSessionQueue.size();
}
