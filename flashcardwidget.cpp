// flashcardwidget.cpp
// Making our flashcard UI come to life!
#include "flashcardwidget.h"
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QMessageBox>
#include <QLocale>
#include <QDebug> // <-- Add this include!

FlashcardWidget::FlashcardWidget(FlashcardSession* session, QWidget *parent)
    : QWidget(parent), m_session(session), m_currentCard(nullptr), m_isFlipped(false) {

    // --- Create Widgets ---
    m_cardTextLabel = new QLabel("Starting session...");
    m_cardTextLabel->setAlignment(Qt::AlignCenter);
    m_cardTextLabel->setWordWrap(true);
    m_cardTextLabel->setStyleSheet("font-size: 24pt; border: 2px solid #f0c0f0; border-radius: 10px; padding: 20px; background-color: white;");

    m_progressLabel = new QLabel("");
    m_progressLabel->setAlignment(Qt::AlignCenter);

    m_flipButton = new QPushButton("Flip Me! ✨");
    m_correctButton = new QPushButton("I knew it! 😊");
    m_incorrectButton = new QPushButton("Oops, try again! 💖");
    m_historyButton = new QPushButton("History! 🕰️"); // Our new button!

    // --- Layout ---
    QVBoxLayout* mainLayout = new QVBoxLayout(this);
    mainLayout->addWidget(m_progressLabel);
    mainLayout->addWidget(m_cardTextLabel, 1); // Give it stretch factor

    QHBoxLayout* buttonLayout = new QHBoxLayout();
    buttonLayout->addWidget(m_incorrectButton);
    buttonLayout->addWidget(m_correctButton);

    mainLayout->addWidget(m_flipButton);
    mainLayout->addLayout(buttonLayout);
    
    // Add the new button below the other buttons
    mainLayout->addWidget(m_historyButton);
    m_historyButton->hide(); // Hide it until we have a card!

    // --- Connections ---
    connect(m_flipButton, &QPushButton::clicked, this, &FlashcardWidget::flipCard);
    connect(m_correctButton, &QPushButton::clicked, this, &FlashcardWidget::onCorrect);
    connect(m_incorrectButton, &QPushButton::clicked, this, &FlashcardWidget::onIncorrect);
    connect(m_historyButton, &QPushButton::clicked, this, &FlashcardWidget::showHistory); // Connect the new button!

    // --- Initial State ---
    showNextCard();
}

FlashcardWidget::~FlashcardWidget() {
    // Clean up the card if the widget is destroyed mid-session
    if(m_currentCard) {
        delete m_currentCard;
    }
}

void FlashcardWidget::showNextCard() {
    m_currentCard = m_session->getNextCard();
    m_isFlipped = false;
    if (m_currentCard) {
        updateUI();
    } else {
        m_cardTextLabel->setText("Yay, session complete! 🎉");
        m_flipButton->hide();
        m_correctButton->hide();
        m_incorrectButton->hide();
        m_historyButton->hide(); // Hide our new button when the session is over
        m_progressLabel->setText("You're a star! 🌟");
    }
}

void FlashcardWidget::updateUI() {
    if (!m_currentCard) return;

    // --- ✨ Here's the new logic to display the example! ✨ ---
    QString text;
    QString example;

    if (m_isFlipped) {
        text = m_currentCard->back;
        example = m_currentCard->backExample;
    } else {
        text = m_currentCard->front;
        example = m_currentCard->frontExample;
    }

    if (!example.isEmpty()) {
        text += QString("<br><br><span style=\"font-style: italic; font-size: 16pt;\">%1</span>").arg(example);
    }
    
    m_cardTextLabel->setText(text);
    m_cardTextLabel->setTextFormat(Qt::RichText);
    m_cardTextLabel->setAlignment(Qt::AlignCenter);

    m_flipButton->setVisible(!m_isFlipped);
    m_correctButton->setVisible(m_isFlipped);
    m_incorrectButton->setVisible(m_isFlipped);
    
    // Show the history button only when we have a card!
    m_historyButton->setVisible(true);

    int total = m_session->totalSessionCards();
    int currentNum = total - m_session->cardsRemaining() - (m_currentCard ? 1 : 0) + 1;
    if (total > 0) {
        m_progressLabel->setText(QString("Card %1 of %2").arg(currentNum).arg(total));
    } else {
        m_progressLabel->setText("No cards due for review today!");
    }
}

void FlashcardWidget::flipCard() {
    m_isFlipped = true;
    updateUI();
}

void FlashcardWidget::onCorrect() {
    m_session->recordAnswer(true);
    showNextCard();
}

void FlashcardWidget::onIncorrect() {
    m_session->recordAnswer(false);
    showNextCard();
}

// Our new function to show the history!
void FlashcardWidget::showHistory() {
    if (!m_currentCard) return;

    // Get the progress from our session manager!
    const FlashcardProgress* progress = m_session->getCardProgress(m_currentCard->id);
    if (!progress) {
        QMessageBox::information(this, "Card History", "No history found for this card.");
        return;
    }

    QString historyText = "💖 **History for this card:** 💖\n\n";
    historyText += QString("Current Box: **%1**\n").arg(progress->box);
    historyText += QString("Next Review: **%1**\n\n").arg(QLocale::system().toString(progress->nextReviewDate, QLocale::LongFormat));
    historyText += "--- **Past Attempts** ---\n";

    if (progress->attempts.isEmpty()) {
        historyText += "This is your first try! Good luck! 😊";
    } else {
        for (const AttemptRecord& attempt : progress->attempts) {
            QString result = attempt.wasCorrect ? "Correct! ✅" : "Incorrect! ❌";
            historyText += QString("• %1: %2\n").arg(QLocale::system().toString(attempt.date, QLocale::ShortFormat)).arg(result);
        }
    }

    QMessageBox msgBox;
    msgBox.setWindowTitle("Card History");
    msgBox.setTextFormat(Qt::RichText);
    msgBox.setText(historyText);
    msgBox.setStandardButtons(QMessageBox::Ok);
    msgBox.setWindowFlags(msgBox.windowFlags() | Qt::FramelessWindowHint);
    msgBox.exec();
}
