#include <QApplication>
#include <QCommandLineParser>
#include <QDir>
#include <QStandardPaths>
#include <QStyleFactory>
#include <QFont>

#include "wifeymoocapp.h"

int main(int argc, char *argv[])
{
    QApplication::setWindowIcon(QIcon(":/icons/wifeymooc.png"));
    // Uncomment to disable GPU video acceleration:
    // QCoreApplication::setAttribute(Qt::AA_UseSoftwareOpenGL);
    QApplication app(argc, argv);
    
    // Set application properties
    app.setApplicationName("Wifey MOOC");
    app.setApplicationVersion("1.0.0");
    app.setApplicationDisplayName("Wifey MOOC");
    app.setOrganizationName("Wifey's Office");
    app.setOrganizationDomain("emily.local");
    
    
    // Set up command line parser
    QCommandLineParser parser;
    parser.setApplicationDescription("A learning MOOC application with interactive questions");
    parser.addHelpOption();
    parser.addVersionOption();
    
    QCommandLineOption questionFileOption(QStringList() << "q" << "question-file",
        "Load questions from <file>.", "file");
    parser.addOption(questionFileOption);
    
    QCommandLineOption progressFileOption(QStringList() << "p" << "progress-file",
        "Load progress from <file>.", "file");
    parser.addOption(progressFileOption);
    
        // NEW: Video resolution options
    QCommandLineOption videoWidthOption("video-width", "Set video width", "width", "1280");
    QCommandLineOption videoHeightOption("video-height", "Set video height", "height", "720");
    parser.addOption(videoWidthOption);
    parser.addOption(videoHeightOption);

    // Process command line arguments
    parser.process(app);

    MediaHandler::s_videoWidth = parser.value(videoWidthOption).toInt();
    MediaHandler::s_videoHeight = parser.value(videoHeightOption).toInt();
    
    QString questionFile = parser.value(questionFileOption);
    QString progressFile = parser.value(progressFileOption);
    
    // Validate file paths if provided
    if (!questionFile.isEmpty() && !QFile::exists(questionFile)) {
        qWarning() << "Question file does not exist:" << questionFile;
        questionFile.clear();
    }
    
    if (!progressFile.isEmpty() && !QFile::exists(progressFile)) {
        qWarning() << "Progress file does not exist:" << progressFile;
        progressFile.clear();
    }
    
    // Set up application styling
    //app.setStyle(QStyleFactory::create("Fusion"));
    
    // Set application font
    QFont font = app.font();
    font.setFamily("Arial");
    font.setPointSize(10);
    app.setFont(font);
    
    // Apply modern dark/light theme
    //QPalette palette = app.palette();
    //palette.setColor(QPalette::Window, QColor(240, 240, 240));
    //palette.setColor(QPalette::WindowText, QColor(0, 0, 0));
    //palette.setColor(QPalette::Base, QColor(255, 255, 255));
    //palette.setColor(QPalette::AlternateBase, QColor(245, 245, 245));
    //palette.setColor(QPalette::ToolTipBase, QColor(255, 255, 220));
    //palette.setColor(QPalette::ToolTipText, QColor(0, 0, 0));
    //palette.setColor(QPalette::Text, QColor(0, 0, 0));
    //palette.setColor(QPalette::Button, QColor(240, 240, 240));
    //palette.setColor(QPalette::ButtonText, QColor(0, 0, 0));
    //palette.setColor(QPalette::BrightText, QColor(255, 0, 0));
    //palette.setColor(QPalette::Link, QColor(0, 0, 255));
    //palette.setColor(QPalette::Highlight, QColor(0, 120, 215));
    //palette.setColor(QPalette::HighlightedText, QColor(255, 255, 255));
    //app.setPalette(palette);
    
    // Create and show main window
    WifeyMOOCApp window(questionFile, progressFile);
    window.show();
    
    return app.exec();
}
