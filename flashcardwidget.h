// flashcardwidget.h
// The cute UI for our flashcard!
#ifndef FLASHCARDWIDGET_H
#define FLASHCARDWIDGET_H

#include <QWidget>
#include <QLabel>
#include <QPushButton>
#include "flashcardsession.h"

class FlashcardWidget : public QWidget {
    Q_OBJECT

public:
    explicit FlashcardWidget(FlashcardSession* session, QWidget *parent = nullptr);
    ~FlashcardWidget();

private slots:
    void flipCard();
    void onCorrect();
    void onIncorrect();

private:
    void showNextCard();
    void updateUI();

    FlashcardSession* m_session;
    const Flashcard* m_currentCard;
    bool m_isFlipped;

    QLabel* m_cardTextLabel;
    QLabel* m_progressLabel;
    QPushButton* m_flipButton;
    QPushButton* m_correctButton;
    QPushButton* m_incorrectButton;
};

#endif // FLASHCARDWIDGET_H
