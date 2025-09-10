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
#include "mediahandler.h"

// --- ✨ A new struct to record every single attempt! ✨ ---
struct AttemptRecord {
    QDateTime date;
    bool wasCorrect;
};

// --- ✨ Our progress struct is now much more detailed! ✨ ---
struct FlashcardProgress {
    QString cardId;
    QString frontText; // So you can read the word in the file!
    QString frontExample; // We added this to save the example!
    QString frontAudio;
    QString backText;  // So you can read the translation!
    QString backExample; // And this to save the back example!
    QString backAudio;
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
    
    const FlashcardProgress* getCardProgress(const QString& cardId) const;
    QString getKvtmlDirectory() const; // ✨ Add this!

private:
    void loadProgress();
    void saveProgress();

    QString progressFilePath;
    QString m_kvtmlDir; // ✨ Our little secret location keeper!
    QList<Flashcard> allCards;
    QMap<QString, FlashcardProgress> progressMap;
    QList<Flashcard> sessionQueue;
    QList<Flashcard> originalSessionQueue;
    const Flashcard* currentCard = nullptr;
};

#endif // FLASHCARDSESSION_H
