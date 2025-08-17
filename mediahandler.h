#ifndef MEDIAHANDLER_H
#define MEDIAHANDLER_H

#include <QObject>
#include <QMediaPlayer>
#include <QAudioOutput>
#include <QVideoWidget>
#include <QLabel>
#include <QJsonObject>
#include <QList>
#include <QPushButton>
#include <QMessageBox>
#include <QUrl>
#include <QDesktopServices>
#include <QProcess>
#include <QScrollArea>
#include <QDialog>
#include <QApplication>
#include <QScreen>
#include <QPixmap>
#include <QPalette>
#include <QVBoxLayout>
#include <QMouseEvent>
#include <QKeyEvent>

class MediaHandler : public QObject
{
    Q_OBJECT
public:
    explicit MediaHandler(QObject *parent = nullptr);
    ~MediaHandler();

    // Media display and playback
    void displayImage(const QString &imagePath, QLabel *imageLabel, int maxWidth = 200);
    void addMediaButtons(const QJsonObject &media, QWidget *parent, const QString &mediaDir);

    // Full screen image display
    void showFullImage(const QString &imagePath, QWidget *parent);

    // Audio/Video playback
    void playAudio(const QString &audioPath);
    void playVideo(const QString &videoPath);
    void stopMedia();

    // Utility
    QString resolveMediaPath(const QString &path, const QString &baseDir);
    bool fileExists(const QString &path);

    //Playback
    void embedAudioPlayer(const QString &audioPath, QWidget *parent);
    void embedVideoPlayer(const QString &videoPath, QWidget *parent, int width = 640, int height = 360);
    static int s_videoWidth;
    static int s_videoHeight;


protected:
    bool eventFilter(QObject *object, QEvent *event) override;

private slots:
    void onPlayAudioClicked();
    void onPlayVideoClicked();
    void onMediaPlayerError();
    void onMediaStatusChanged();

private:
    void launchExternalPlayer(const QString &filePath);
    void createImagePreviewDialog(const QString &imagePath, QWidget *parent);

    QMediaPlayer *m_mediaPlayer;
    QAudioOutput *m_audioOutput;
    QWidget *m_videoWidget;
    QString m_currentAudioPath;
    QString m_currentVideoPath;
    QString m_baseMediaDir;

    QList<QPushButton*> m_mediaButtons;

    static constexpr int DEFAULT_IMAGE_WIDTH = 200;
    static constexpr int PREVIEW_MAX_WIDTH   = 800;
    static constexpr int PREVIEW_MAX_HEIGHT  = 600;
};

#endif // MEDIAHANDLER_H
