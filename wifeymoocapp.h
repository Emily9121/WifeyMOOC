#ifndef WIFEYMOOCAPP_H
#define WIFEYMOOCAPP_H

#include <QMainWindow>
#include <QWidget>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QGridLayout>
#include <QLabel>
#include <QPushButton>
#include <QRadioButton>
#include <QCheckBox>
#include <QLineEdit>
#include <QTextEdit>
#include <QComboBox>
#include <QListWidget>
#include <QScrollArea>
#include <QMenuBar>
#include <QStatusBar>
#include <QFileDialog>
#include <QMessageBox>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <QJsonValue>
#include <QVariantMap>
#include <QPixmap>
#include <QMouseEvent>
#include <QPaintEvent>
#include <QDragEnterEvent>
#include <QDragMoveEvent>
#include <QDropEvent>
#include <QMimeData>
#include <QDrag>
#include <QButtonGroup>
#include <QStackedWidget>
#include <QSplitter>
#include <QProcess>
#include <QUrl>
#include <QDesktopServices>
#include <QTimer>
#include <QProgressBar>
#include <QSpinBox>
#include <QGroupBox>
#include <QFrame>
#include <QApplication>
#include <QScreen>
#include <QStandardPaths>
#include <QDir>

#include "questionhandlers.h"
#include "mediahandler.h"

class WifeyMOOCApp : public QMainWindow
{
    Q_OBJECT

public:
    WifeyMOOCApp(const QString &questionFile = QString(), 
                 const QString &progressFile = QString(), 
                 QWidget *parent = nullptr);
    ~WifeyMOOCApp();

private slots:
    void loadQuestions();
    void saveProgress();
    void loadProgress();
    void checkAnswer();
    void nextQuestion();
    void skipQuestion();
    void showFullImage(const QString &imagePath);
    void showHint(); 
    void viewLessonPdf(); // ✨ CORRECTED: The new slot for viewing the PDF! ✨


protected:
    void closeEvent(QCloseEvent *event) override;

private:
    void setupUI();
    void setupMenuBar();
    void clearWidgets();
    void displayWelcome();
    void displayQuestion();
    void displayCompleted();
    bool loadQuestionsFromFile(const QString &filePath);
    bool loadProgressFromFile(const QString &filePath);
    bool saveProgressToFile(const QString &filePath);
    QString resolveMediaPath(const QString &path);
    void resetScrollArea();
    void updateProgress();

    // UI Components
    QWidget *m_centralWidget;
    QVBoxLayout *m_mainLayout;
    
    QLabel *m_questionLabel;
    QScrollArea *m_scrollArea;
    QWidget *m_scrollContent;
    QVBoxLayout *m_scrollLayout;
    
    QWidget *m_buttonPanel;
    QHBoxLayout *m_buttonLayout;
    QPushButton *m_submitButton;
    QPushButton *m_nextButton;
    QPushButton *m_skipButton;  
    QPushButton *m_altImageButton; 
    QPushButton *m_hintButton; 
    QPushButton *m_lessonButton; // ✨ ADDED: Our new button for the lesson PDF! ✨
    QLabel *m_feedbackLabel;
    QProgressBar *m_progressBar;
    
    // Question handling
    QJsonArray m_questions;
    int m_currentQuestion;
    int m_score;
    QVariantMap m_studentAnswers;
    QString m_currentQuestionFile;
    QString m_progressFile;
    QString m_jsonDir;
    QString m_currentHint;
    QString m_currentLessonPdfPath; // ✨ ADDED: The path for the current lesson PDF! ✨
    
    // Question handlers
    QuestionHandlers *m_questionHandlers;
    MediaHandler *m_mediaHandler;
    
    // Image tagging specific
    QVariantMap m_tagPositions;
    int m_imageTaggingAltIndex;
    
    // State
    bool m_questionsLoaded;
    bool m_enableSkipButton;
    
    // Constants
    static constexpr int PADDING_X = 6;
    static constexpr int PADDING_Y = 3;
    static constexpr int TAG_START_X = 10;
    static constexpr int TAG_START_Y = 10;
    static constexpr int RESERVED_HEIGHT = 160;
    static constexpr bool DEBUG = true;
};

#endif // WIFEYMOOCAPP_H
