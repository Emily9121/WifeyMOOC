// flashcardwidget.cpp
// Making our flashcard UI come to life!
#include "flashcardwidget.h"
#include <QVBoxLayout>
#include <QHBoxLayout>

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
    m_incorrectButton = new QPushButton("Oops, try again! 🤔");

    // --- Layout ---
    QVBoxLayout* mainLayout = new QVBoxLayout(this);
    mainLayout->addWidget(m_progressLabel);
    mainLayout->addWidget(m_cardTextLabel, 1); // Give it stretch factor

    QHBoxLayout* buttonLayout = new QHBoxLayout();
    buttonLayout->addWidget(m_incorrectButton);
    buttonLayout->addWidget(m_correctButton);

    mainLayout->addWidget(m_flipButton);
    mainLayout->addLayout(buttonLayout);
    
    // --- Connections ---
    connect(m_flipButton, &QPushButton::clicked, this, &FlashcardWidget::flipCard);
    connect(m_correctButton, &QPushButton::clicked, this, &FlashcardWidget::onCorrect);
    connect(m_incorrectButton, &QPushButton::clicked, this, &FlashcardWidget::onIncorrect);

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
        m_progressLabel->setText("You're a star! 🌟");
    }
}

void FlashcardWidget::updateUI() {
    if (!m_currentCard) return;

    m_cardTextLabel->setText(m_isFlipped ? m_currentCard->back : m_currentCard->front);
    m_flipButton->setVisible(!m_isFlipped);
    m_correctButton->setVisible(m_isFlipped);
    m_incorrectButton->setVisible(m_isFlipped);
    
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