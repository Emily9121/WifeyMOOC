#include "wifeymoocapp.h"
#include <QApplication>
#include <QCloseEvent>
#include <QStandardPaths>
#include <QDir>
#include <QScrollBar>

WifeyMOOCApp::WifeyMOOCApp(const QString &questionFile, 
                           const QString &progressFile, 
                           QWidget *parent)
    : QMainWindow(parent)
    , m_centralWidget(nullptr)
    , m_mainLayout(nullptr)
    , m_questionLabel(nullptr)
    , m_scrollArea(nullptr)
    , m_scrollContent(nullptr)
    , m_scrollLayout(nullptr)
    , m_buttonPanel(nullptr)
    , m_buttonLayout(nullptr)
    , m_submitButton(nullptr)
    , m_nextButton(nullptr)
    , m_skipButton(nullptr)
    , m_altImageButton(nullptr)
    , m_feedbackLabel(nullptr)
    , m_progressBar(nullptr)
    , m_currentQuestion(0)
    , m_score(0)
    , m_questionHandlers(nullptr)
    , m_mediaHandler(nullptr)
    , m_imageTaggingAltIndex(0)
    , m_questionsLoaded(false)
    , m_enableSkipButton(DEBUG)
{
    #ifdef Q_OS_LINUX
    setWindowTitle("WifeyMOOC 1.0.4 for Linux");
    #elif defined(Q_OS_WINDOWS)
        setWindowTitle("WifeyMOOC 1.0.4 for Windows");
    #elif defined(Q_OS_MACOS)
        setWindowTitle("WifeyMOOC 1.0.4 for macOS");
    #else
        setWindowTitle("WifeyMOOC 1.0.4 on Unsupported OS");
    #endif

    setMinimumSize(1000, 700);
    
    setupUI();
    setupMenuBar();
    
    // Initialize handlers
    m_questionHandlers = new QuestionHandlers(this);
    m_mediaHandler = new MediaHandler(this);
    
    // Load initial files if provided
    if (!progressFile.isEmpty()) {
        if (!loadProgressFromFile(progressFile)) {
            if (!questionFile.isEmpty()) {
                loadQuestionsFromFile(questionFile);
            } else {
                displayWelcome();
            }
        }
    } else if (!questionFile.isEmpty()) {
        loadQuestionsFromFile(questionFile);
    } else {
        displayWelcome();
    }
}

WifeyMOOCApp::~WifeyMOOCApp()
{
}

void WifeyMOOCApp::setupUI()
{
    m_centralWidget = new QWidget;
    setCentralWidget(m_centralWidget);
    
    m_mainLayout = new QVBoxLayout(m_centralWidget);
    m_mainLayout->setSpacing(10);
    m_mainLayout->setContentsMargins(10, 10, 10, 10);
    
    // Question label
    m_questionLabel = new QLabel;
    m_questionLabel->setFont(QFont("Arial", 14, QFont::Bold));
    m_questionLabel->setWordWrap(true);
    m_questionLabel->setAlignment(Qt::AlignLeft | Qt::AlignTop);
    m_mainLayout->addWidget(m_questionLabel);
    
    // Progress bar
    m_progressBar = new QProgressBar;
    m_progressBar->setVisible(false);
    m_mainLayout->addWidget(m_progressBar);
    
    // Scroll area for question content
    m_scrollArea = new QScrollArea;
    m_scrollArea->setWidgetResizable(true);
    m_scrollArea->setHorizontalScrollBarPolicy(Qt::ScrollBarAsNeeded);
    m_scrollArea->setVerticalScrollBarPolicy(Qt::ScrollBarAsNeeded);
    
    m_scrollContent = new QWidget;
    m_scrollLayout = new QVBoxLayout(m_scrollContent);
    m_scrollLayout->setAlignment(Qt::AlignTop);
    m_scrollArea->setWidget(m_scrollContent);
    
    m_mainLayout->addWidget(m_scrollArea, 1); // Takes most space
    
    // Button panel
    m_buttonPanel = new QWidget;
    m_buttonLayout = new QHBoxLayout(m_buttonPanel);
    
    // Feedback label
    m_feedbackLabel = new QLabel;
    m_feedbackLabel->setFont(QFont("Arial", 12));
    m_feedbackLabel->setStyleSheet("color: red;");
    m_buttonLayout->addWidget(m_feedbackLabel);
    
    m_buttonLayout->addStretch(); // Push buttons to the right
    
    // Alternative image button (for image_tagging)
    m_altImageButton = new QPushButton("Alternative Version");
    m_altImageButton->setVisible(false);
    connect(m_altImageButton, &QPushButton::clicked, this, [this]() {
        // --- FIX: Save all current positions before changing alternative ---
        m_tagPositions = m_questionHandlers->getTagPositions();

        int maxAlts = 1;
        if(m_questionsLoaded && m_currentQuestion < m_questions.size()) {
            QJsonObject question = m_questions[m_currentQuestion].toObject();
            if(question["type"].toString() == "image_tagging") {
                QJsonArray alts = question.value("alternatives").toArray();
                maxAlts = alts.size() + 1;
            }
        }

        m_imageTaggingAltIndex = (m_imageTaggingAltIndex + 1) % maxAlts;
        displayQuestion();
    });
    m_buttonLayout->addWidget(m_altImageButton);
    
    // Submit button
    m_submitButton = new QPushButton("Submit Answer");
    m_submitButton->setEnabled(false);
    connect(m_submitButton, &QPushButton::clicked, this, &WifeyMOOCApp::checkAnswer);
    m_buttonLayout->addWidget(m_submitButton);
    
    // Next button
    m_nextButton = new QPushButton("Next Question");
    m_nextButton->setEnabled(false);
    connect(m_nextButton, &QPushButton::clicked, this, &WifeyMOOCApp::nextQuestion);
    m_buttonLayout->addWidget(m_nextButton);
    
    // Skip button (debug)
    if (m_enableSkipButton) {
        m_skipButton = new QPushButton("SKIP (DEBUG)");
        m_skipButton->setStyleSheet("background-color: red; color: white; font-weight: bold;");
        connect(m_skipButton, &QPushButton::clicked, this, &WifeyMOOCApp::skipQuestion);
        m_buttonLayout->addWidget(m_skipButton);
    }
    
    m_mainLayout->addWidget(m_buttonPanel);
}

void WifeyMOOCApp::setupMenuBar()
{
    QMenuBar *menuBar = this->menuBar();
    
    QMenu *fileMenu = menuBar->addMenu("&File");
    
    QAction *loadQuestionsAction = fileMenu->addAction("&Load Questions");
    loadQuestionsAction->setShortcut(QKeySequence::Open);
    connect(loadQuestionsAction, &QAction::triggered, this, &WifeyMOOCApp::loadQuestions);
    
    fileMenu->addSeparator();
    
    QAction *saveProgressAction = fileMenu->addAction("&Save Progress");
    saveProgressAction->setShortcut(QKeySequence::Save);
    connect(saveProgressAction, &QAction::triggered, this, &WifeyMOOCApp::saveProgress);
    
    QAction *loadProgressAction = fileMenu->addAction("Load &Progress");
    connect(loadProgressAction, &QAction::triggered, this, &WifeyMOOCApp::loadProgress);
    
    fileMenu->addSeparator();
    
    QAction *exitAction = fileMenu->addAction("E&xit");
    exitAction->setShortcut(QKeySequence::Quit);
    connect(exitAction, &QAction::triggered, this, &QWidget::close);
}

void WifeyMOOCApp::clearWidgets()
{
    m_questionLabel->clear();
    m_feedbackLabel->clear();
    m_feedbackLabel->setStyleSheet("color: red;");
    
    // Clear scroll area content
    QLayoutItem *child;
    while ((child = m_scrollLayout->takeAt(0)) != nullptr) {
        if (child->widget()) {
            child->widget()->deleteLater();
        }
        delete child;
    }
    
    m_submitButton->setEnabled(false);
    m_nextButton->setEnabled(false);
    m_altImageButton->setVisible(false);
    
    resetScrollArea();
    
    if (m_questionHandlers) {
        m_questionHandlers->clearCurrentQuestion();
    }
}

void WifeyMOOCApp::displayWelcome()
{
    clearWidgets();
    if (m_mediaHandler)
    m_mediaHandler->stopMedia();
    m_questionLabel->setText("Welcome to Wifey MOOC!\n\nFuck around a question file to start finding out.");
    
    QPushButton *loadBtn = new QPushButton("Load Questions");
    loadBtn->setFont(QFont("Arial", 14, QFont::Bold));
    loadBtn->setMinimumHeight(40);
    connect(loadBtn, &QPushButton::clicked, this, &WifeyMOOCApp::loadQuestions);
    
    m_scrollLayout->addWidget(loadBtn);
    m_scrollLayout->addStretch();
}

void WifeyMOOCApp::displayQuestion()
{
    clearWidgets();
    if (m_mediaHandler)
    m_mediaHandler->stopMedia();

    if (!m_questionsLoaded || m_currentQuestion >= m_questions.size()) {
        displayCompleted();
        return;
    }

    QJsonObject question = m_questions[m_currentQuestion].toObject();

    // Update question label
    QString questionText = QString("Q%1: %2")
                              .arg(m_currentQuestion + 1)
                              .arg(question["question"].toString());
    m_questionLabel->setText(questionText);

    // Update progress
    updateProgress();

    // ---- Begin new robust code ----

    // Make a container for media + question input
    QWidget *container = new QWidget;
    QVBoxLayout *containerLayout = new QVBoxLayout(container);
    containerLayout->setAlignment(Qt::AlignTop);
    containerLayout->setContentsMargins(0, 0, 0, 0);

    // Pass container as 'parent' so media handler adds media UI to this layout.
    QWidget *questionWidget = m_questionHandlers->createQuestionWidget(
        question, container, m_jsonDir, m_mediaHandler, m_imageTaggingAltIndex);

    // The media handler will have already injected any media controls into the container's layout at this point.

    // Now, ALWAYS add the returned questionWidget to the container's layout
    // (Unless it's nullptr or container itself)
    if (questionWidget && questionWidget != container) {
        containerLayout->addWidget(questionWidget);
    }

    // ---- Place these here ----
    // 1. Update Alt Button UI
    // ---- 1. Update Alt Button UI ----
    if (question["type"].toString() == "image_tagging") {
        // Gather labels: main first, then each alternative
        QStringList labels;
        labels << question.value("button_label").toString("Alternative Version");
        QJsonArray alts = question.value("alternatives").toArray();
        for (const QJsonValue &altVal : alts) {
            QJsonObject alt = altVal.toObject();
            labels << alt.value("button_label").toString(QString("Alternative %1").arg(labels.size()));
        }

        int altCount = labels.size();
        int idx = m_imageTaggingAltIndex;
        if (altCount > 1) {
            // Sanity: wrap index in case of OOB
            if (idx < 0 || idx >= altCount) idx = 0;
            m_altImageButton->setText(labels[idx]);
            m_altImageButton->setVisible(true);
        } else {
            m_altImageButton->setVisible(false);
        }
    } else {
        m_altImageButton->setVisible(false);
    }

    // --- Enable submit button and update alt logic as usual ---
    m_submitButton->setEnabled(true);
    if (question["type"].toString() == "image_tagging") {
        // Use consistent logic: rely on label count above
        int idx = m_imageTaggingAltIndex;
        QStringList labels;
        labels << question.value("button_label").toString("Alternative Version");
        QJsonArray alts = question.value("alternatives").toArray();
        for (const QJsonValue &altVal : alts) {
            QJsonObject alt = altVal.toObject();
            labels << alt.value("button_label").toString(QString("Alternative %1").arg(labels.size()));
        }
        int altCount = labels.size();
        if (altCount > 1) {
            if (idx < 0 || idx >= altCount) idx = 0;
            m_altImageButton->setText(labels[idx]);
            m_altImageButton->setVisible(true);
        } else {
            m_altImageButton->setVisible(false);
        }
    } else {
        m_altImageButton->setVisible(false);
    }

    // Add the complete container (media + answer controls) to the scroll area
    m_scrollLayout->addWidget(container);
    m_scrollLayout->addStretch();
    container->show();

    // Enable submit button and alternative image logic as usual
    m_submitButton->setEnabled(true);

    if (question["type"].toString() == "image_tagging") {
        // Build label list: main label then each alternative
        QStringList labels;
        labels << question.value("button_label").toString("Alternative Version");
        QJsonArray alts = question.value("alternatives").toArray();
        for (const QJsonValue &altVal : alts) {
            QJsonObject alt = altVal.toObject();
            labels << alt.value("button_label").toString(QString("Alternative %1").arg(labels.size()));
        }
        int altCount = labels.size();
        int idx = m_imageTaggingAltIndex;
        if (altCount > 1) {
            // Wrap index in case of out-of-bounds
            if (idx < 0 || idx >= altCount) idx = 0;
            m_altImageButton->setText(labels[idx]);
            m_altImageButton->setVisible(true);
        } else {
            m_altImageButton->setVisible(false);
        }
    } else {
        m_altImageButton->setVisible(false);
    }
}



void WifeyMOOCApp::displayCompleted()
{
    clearWidgets();
    if (m_mediaHandler)
    m_mediaHandler->stopMedia();
    int totalQuestions = m_questions.size();
    QString completionText = QString("🎉 Quiz Completed! 🎉\n\n"
                                   "Your Score: %1/%2 (%3%)\n\n"
                                   "Congratulations on completing the French learning quiz!")
                            .arg(m_score)
                            .arg(totalQuestions)
                            .arg(totalQuestions > 0 ? (m_score * 100) / totalQuestions : 0);
    
    m_questionLabel->setText(completionText);
    m_questionLabel->setAlignment(Qt::AlignCenter);
    
    // Create restart button
    QPushButton *restartBtn = new QPushButton("Restart Quiz");
    restartBtn->setFont(QFont("Arial", 14, QFont::Bold));
    restartBtn->setMinimumHeight(40);
    connect(restartBtn, &QPushButton::clicked, this, [this]() {
        m_currentQuestion = 0;
        m_score = 0;
        m_studentAnswers.clear();
        displayQuestion();
    });
    
    QPushButton *loadNewBtn = new QPushButton("Load New Questions");
    loadNewBtn->setFont(QFont("Arial", 12));
    loadNewBtn->setMinimumHeight(40);
    connect(loadNewBtn, &QPushButton::clicked, this, &WifeyMOOCApp::loadQuestions);
    
    QHBoxLayout *buttonLayout = new QHBoxLayout;
    buttonLayout->addStretch();
    buttonLayout->addWidget(restartBtn);
    buttonLayout->addWidget(loadNewBtn);
    buttonLayout->addStretch();
    
    QWidget *buttonWidget = new QWidget;
    buttonWidget->setLayout(buttonLayout);
    
    m_scrollLayout->addStretch();
    m_scrollLayout->addWidget(buttonWidget);
    m_scrollLayout->addStretch();
    
    // Show final score in progress bar
    if (totalQuestions > 0) {
        m_progressBar->setVisible(true);
        m_progressBar->setValue((m_score * 100) / totalQuestions);
        m_progressBar->setFormat(QString("Final Score: %1/%2").arg(m_score).arg(totalQuestions));
    }
}

bool WifeyMOOCApp::loadQuestionsFromFile(const QString &filePath)
{
    QFile file(filePath);
    if (!file.open(QIODevice::ReadOnly)) {
        QMessageBox::critical(this, "Error", 
                             QString("Failed to open file:\n%1").arg(filePath));
        return false;
    }
    
    QJsonParseError error;
    QJsonDocument doc = QJsonDocument::fromJson(file.readAll(), &error);
    
    if (error.error != QJsonParseError::NoError) {
        QMessageBox::critical(this, "JSON Parse Error", 
                             QString("Failed to parse JSON:\n%1").arg(error.errorString()));
        return false;
    }
    
    if (!doc.isArray()) {
        QMessageBox::critical(this, "Format Error", "JSON file must contain an array of questions.");
        return false;
    }
    
    m_questions = doc.array();
    m_currentQuestionFile = filePath;
    m_jsonDir = QFileInfo(filePath).absolutePath();
    m_currentQuestion = 0;
    m_score = 0;
    m_studentAnswers.clear();
    m_questionsLoaded = true;
    
    displayQuestion();
    return true;
}

bool WifeyMOOCApp::loadProgressFromFile(const QString &filePath)
{
    QFile file(filePath);
    if (!file.open(QIODevice::ReadOnly)) {
        QMessageBox::critical(this, "Error", 
                             QString("Failed to open progress file:\n%1").arg(filePath));
        return false;
    }
    
    QJsonParseError error;
    QJsonDocument doc = QJsonDocument::fromJson(file.readAll(), &error);
    
    if (error.error != QJsonParseError::NoError) {
        QMessageBox::critical(this, "JSON Parse Error", 
                             QString("Failed to parse progress file:\n%1").arg(error.errorString()));
        return false;
    }
    
    QJsonObject progressData = doc.object();
    QString questionFile = progressData["question_file"].toString();
    
    if (questionFile.isEmpty() || !QFileInfo::exists(questionFile)) {
        QMessageBox::critical(this, "Load Error", 
                             "Quiz file missing or not specified in progress file.");
        return false;
    }
    
    // Load the questions first
    if (!loadQuestionsFromFile(questionFile)) {
        return false;
    }
    
    // Restore progress
    m_currentQuestion = progressData["current_question"].toInt();
    m_score = progressData["score"].toInt();
    m_studentAnswers = progressData["student_answers"].toObject().toVariantMap();
    
    // Load tag positions for image_tagging
    if (progressData.contains("tag_positions_dict")) {
        QJsonObject tagPositionsObj = progressData["tag_positions_dict"].toObject();
        for (auto it = tagPositionsObj.begin(); it != tagPositionsObj.end(); ++it) {
            m_tagPositions[it.key()] = it.value().toObject().toVariantMap();
        }
        m_questionHandlers->setTagPositions(m_tagPositions);
    }
    
    m_progressFile = filePath;
    
    displayQuestion();
    return true;
}

bool WifeyMOOCApp::saveProgressToFile(const QString &filePath)
{
    if (m_currentQuestionFile.isEmpty()) {
        QMessageBox::warning(this, "Save Progress", "No quiz loaded.");
        return false;
    }
    
    QJsonObject progressData;
    progressData["current_question"] = m_currentQuestion;
    progressData["score"] = m_score;
    progressData["question_file"] = m_currentQuestionFile;
    
    // Convert student answers to JSON
    QJsonObject studentAnswersObj;
    for (auto it = m_studentAnswers.begin(); it != m_studentAnswers.end(); ++it) {
        studentAnswersObj[it.key()] = QJsonValue::fromVariant(it.value());
    }
    progressData["student_answers"] = studentAnswersObj;
    
    // Save tag positions
    QVariantMap tagPositions = m_questionHandlers->getTagPositions();
    QJsonObject tagPositionsObj;
    for (auto it = tagPositions.begin(); it != tagPositions.end(); ++it) {
        QJsonObject posObj;
        QVariantMap posMap = it.value().toMap();
        for (auto posIt = posMap.begin(); posIt != posMap.end(); ++posIt) {
            posObj[posIt.key()] = QJsonValue::fromVariant(posIt.value());
        }
        tagPositionsObj[it.key()] = posObj;
    }
    progressData["tag_positions_dict"] = tagPositionsObj;
    
    QJsonDocument doc(progressData);
    
    QFile file(filePath);
    if (!file.open(QIODevice::WriteOnly)) {
        QMessageBox::critical(this, "Save Error", 
                             QString("Could not save progress:\n%1").arg(file.errorString()));
        return false;
    }
    
    file.write(doc.toJson());
    QMessageBox::information(this, "Save Progress", "Progress saved successfully.");
    return true;
}

QString WifeyMOOCApp::resolveMediaPath(const QString &path)
{
    if (QFileInfo(path).isAbsolute()) {
        return path;
    }
    
    if (!m_jsonDir.isEmpty()) {
        return QDir(m_jsonDir).absoluteFilePath(path);
    }
    
    return path;
}

void WifeyMOOCApp::resetScrollArea()
{
    m_scrollArea->verticalScrollBar()->setValue(0);
    m_scrollArea->horizontalScrollBar()->setValue(0);
}

void WifeyMOOCApp::updateProgress()
{
    if (m_questionsLoaded && m_questions.size() > 0) {
        m_progressBar->setVisible(true);
        m_progressBar->setMaximum(m_questions.size());
        m_progressBar->setValue(m_currentQuestion);
        m_progressBar->setFormat(QString("Question %1 of %2")
                                .arg(m_currentQuestion + 1)
                                .arg(m_questions.size()));
    } else {
        m_progressBar->setVisible(false);
    }
}

// Slot implementations
void WifeyMOOCApp::loadQuestions()
{
    QString fileName = QFileDialog::getOpenFileName(
        this,
        "Load Questions",
        QStandardPaths::writableLocation(QStandardPaths::DocumentsLocation),
        "JSON files (*.json);;All files (*.*)"
    );
    
    if (!fileName.isEmpty()) {
        loadQuestionsFromFile(fileName);
    }
}

void WifeyMOOCApp::saveProgress()
{
    if (!m_questionsLoaded) {
        QMessageBox::warning(this, "Save Progress", "No quiz loaded.");
        return;
    }
    
    QString fileName = QFileDialog::getSaveFileName(
        this,
        "Save Progress",
        QStandardPaths::writableLocation(QStandardPaths::DocumentsLocation) + "/progress.json",
        "JSON files (*.json);;All files (*.*)"
    );
    
    if (!fileName.isEmpty()) {
        saveProgressToFile(fileName);
    }
}

void WifeyMOOCApp::loadProgress()
{
    QString fileName = QFileDialog::getOpenFileName(
        this,
        "Load Progress",
        QStandardPaths::writableLocation(QStandardPaths::DocumentsLocation),
        "JSON files (*.json);;All files (*.*)"
    );
    
    if (!fileName.isEmpty()) {
        loadProgressFromFile(fileName);
    }
}

void WifeyMOOCApp::checkAnswer()
{
    if (!m_questionsLoaded || m_currentQuestion >= m_questions.size()) {
        return;
    }
    
    QJsonObject question = m_questions[m_currentQuestion].toObject();
    QuestionResult result = m_questionHandlers->checkAnswer(question);
    
    if (result.isCorrect) {
        m_feedbackLabel->setText("Correct! ✓");
        m_feedbackLabel->setStyleSheet("color: green; font-weight: bold;");
        
        m_submitButton->setEnabled(false);
        m_nextButton->setEnabled(true);
        
        // Award points only once per question
        QString questionKey = QString::number(m_currentQuestion);
        if (!m_studentAnswers.contains(questionKey)) {
            m_score++;
        }
        m_studentAnswers[questionKey] = result.userAnswer;
        
    } else {
        m_feedbackLabel->setText(result.message.isEmpty() ? "Incorrect, please try again. ✗" : result.message);
        m_feedbackLabel->setStyleSheet("color: red; font-weight: bold;");
    }
}

void WifeyMOOCApp::nextQuestion()
{
    m_currentQuestion++;
    if (m_currentQuestion >= m_questions.size()) {
        displayCompleted();
    } else {
        displayQuestion();
    }
}

void WifeyMOOCApp::skipQuestion()
{
    if (DEBUG) {
        nextQuestion();
    }
}

void WifeyMOOCApp::showFullImage(const QString &imagePath)
{
    if (m_mediaHandler) {
        m_mediaHandler->showFullImage(resolveMediaPath(imagePath), this);
    }
}

void WifeyMOOCApp::closeEvent(QCloseEvent *event)
{
    // Optional: Auto-save progress on close
    if (m_questionsLoaded && !m_progressFile.isEmpty()) {
        saveProgressToFile(m_progressFile);
    }
    
    QMainWindow::closeEvent(event);
}
