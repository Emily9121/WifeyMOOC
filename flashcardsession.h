// flashcardsession.h
// This class is the brain! It manages the learning progress.
#ifndef FLASHCARDSESSION_H
#define FLASHCARDSESSION_H

#include "parleyparser.h"
#include <QObject>
#include <QDateTime>
#include <QJsonObject>
#include <QJsonDocument>
#include <QJsonArray>
#include <QFile>
#include <QDir>

// --- ✨ A new struct to record every single attempt! ✨ ---
struct AttemptRecord {
    QDateTime date;
    bool wasCorrect;
};

// --- ✨ Our progress struct is now much more detailed! ✨ ---
struct FlashcardProgress {
    QString cardId;
    QString frontText; // So you can read the word in the file!
    QString backText;  // So you can read the translation!
    int box = 1;
    QDateTime nextReviewDate;
    QList<AttemptRecord> attempts; // A full history of every try!
};

class FlashcardSession : public QObject {
    Q_OBJECT

public:
    explicit FlashcardSession(const QList<Flashcard>& allCards, const QString& parleyFilePath, QObject *parent = nullptr);

    void startSession(int sessionSize);
    const Flashcard* getNextCard();
    void recordAnswer(bool wasCorrect);
    int cardsRemaining() const;
    int totalSessionCards() const;
    
    // The missing method!
    const FlashcardProgress* getCardProgress(const QString& cardId) const;

private:
    void loadProgress();
    void saveProgress();

    QString progressFilePath;
    QList<Flashcard> allCards;
    QMap<QString, FlashcardProgress> progressMap;
    QList<Flashcard> sessionQueue;
    QList<Flashcard> originalSessionQueue;
    const Flashcard* currentCard = nullptr;
};

#endif // FLASHCARDSESSION_H
