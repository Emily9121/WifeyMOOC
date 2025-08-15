#ifndef QUESTIONHANDLERS_H
#define QUESTIONHANDLERS_H

#include <QObject>
#include <QWidget>
#include <QVariant>
#include <QJsonObject>
#include <QJsonArray>
#include <QButtonGroup>
#include <QList>
#include <QListWidget>
#include <QComboBox>
#include <QLabel>
#include <QLineEdit>
#include <QSpinBox>
#include <QPushButton>
#include <QSet>
#include <QCheckBox>
#include "droptag.h" // For ImageTaggingWidget

class MediaHandler;

struct QuestionResult {
    bool isCorrect = false;
    QVariant userAnswer;
    QString message;
};

class QuestionHandlers : public QObject
{
    Q_OBJECT
public:
    explicit QuestionHandlers(QObject *parent = nullptr);

    QWidget* createQuestionWidget(const QJsonObject &question,
        QWidget *parent = nullptr,
        const QString &mediaDir = QString(),
        MediaHandler *mediaHandler = nullptr,
        int imageTaggingAltIndex = 0); // <-- ADD THIS ARG

    QuestionResult checkAnswer(const QJsonObject &question);
    void clearCurrentQuestion();

    void setImageTaggingAlternative(int altIndex);
    int getImageTaggingAlternativeCount() const;

    void setTagPositions(const QVariantMap &positions);
    QVariantMap getTagPositions() const;

public:
    void addMediaButtons(const QJsonObject &media, QWidget *parent);

private:
    // Question type handlers
    QWidget* createMcqSingle(const QJsonObject &question, QWidget *parent);
    QWidget* createMcqMultiple(const QJsonObject &question, QWidget *parent);
    QWidget* createWordFill(const QJsonObject &question, QWidget *parent);
    QWidget* createListPick(const QJsonObject &question, QWidget *parent);
    QWidget* createMatchSentence(const QJsonObject &question, QWidget *parent);
    QWidget* createCategorization(const QJsonObject &question, QWidget *parent);
    QWidget* createCategorizationMultiple(const QJsonObject &question, QWidget *parent);
    QWidget* createSequenceAudio(const QJsonObject &question, QWidget *parent);
    QWidget* createOrderPhrase(const QJsonObject &question, QWidget *parent);
    QWidget* createFillBlanksDropdown(const QJsonObject &question, QWidget *parent);
    QWidget* createMatchPhrases(const QJsonObject &question, QWidget *parent);
    QWidget* createImageTagging(const QJsonObject &question, QWidget *parent);

    // Answer checkers
    QuestionResult checkMcqSingle(const QJsonObject &question);
    QuestionResult checkMcqMultiple(const QJsonObject &question);
    QuestionResult checkWordFill(const QJsonObject &question);
    QuestionResult checkListPick(const QJsonObject &question);
    QuestionResult checkMatchSentence(const QJsonObject &question);
    QuestionResult checkCategorization(const QJsonObject &question);
    QuestionResult checkCategorizationMultiple(const QJsonObject &question);
    QuestionResult checkSequenceAudio(const QJsonObject &question);
    QuestionResult checkOrderPhrase(const QJsonObject &question);
    QuestionResult checkFillBlanksDropdown(const QJsonObject &question);
    QuestionResult checkMatchPhrases(const QJsonObject &question);
    QuestionResult checkImageTagging(const QJsonObject &question);

    // Helpers
    QString resolveImagePath(const QString &path) const;

    // Clanker Edit
    void moveOrderPhraseWord(int index, int direction);

    // State
    QString m_currentQuestionType;
    QWidget *m_currentQuestionWidget;
    QJsonObject m_currentQuestion;
    QString m_mediaDir;
    MediaHandler *m_mediaHandler;

    // UI storage
    QButtonGroup *m_mcqButtonGroup;
    QList<QCheckBox*> m_mcqCheckBoxes;
    QList<QLineEdit*> m_wordFillEntries;
    QListWidget *m_listPickWidget;
    QList<QComboBox*> m_matchComboBoxes;
    QComboBox *m_categorizationCombo;
    QList<QComboBox*> m_multipleCategorizationCombos;
    QList<QSpinBox*> m_sequenceSpinBoxes;
    QList<QPushButton*> m_orderPhraseWords;
    QList<QLabel*> m_orderPhraseLabels;
    QList<QComboBox*> m_fillBlanksDropdowns;
    QList<QComboBox*> m_matchPhraseCombos;

    // Image tagging
    ImageTaggingWidget *m_imageTaggingWidget;
    QList<DropTag*> m_dropTags;
    QLabel *m_imageLabel;
    QVariantMap m_tagPositions;
    int m_imageTaggingAltIndex;
    QJsonArray m_imageTaggingAlternatives;

    QLineEdit *m_lastFocusedEntry;
signals:
    void answerChanged();
    void imageTaggingAlternativeChanged(int newIndex);
};

#endif // QUESTIONHANDLERS_H
