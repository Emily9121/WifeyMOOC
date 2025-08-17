#include "mediahandler.h"

#include <QDir>
#include <QStandardPaths>
#include <QFileInfo>
#include <QUrl>
#include <QMouseEvent>
#include <QKeyEvent>
#include <QStyle>
#include <QTimer>
#include <QSlider>
#include <QBoxLayout>
#include <QLabel>
#include <QPushButton>
#include <QGraphicsView>
#include <QGraphicsScene>
#include <QGraphicsVideoItem>

int MediaHandler::s_videoWidth = 1280;
int MediaHandler::s_videoHeight = 720;

MediaHandler::MediaHandler(QObject *parent)
: QObject(parent),
m_mediaPlayer(new QMediaPlayer(this)),
m_audioOutput(new QAudioOutput(this)),
m_videoWidget(nullptr)
{
    m_mediaPlayer->setAudioOutput(m_audioOutput);
    connect(m_mediaPlayer, &QMediaPlayer::errorOccurred,
            this, &MediaHandler::onMediaPlayerError);
    connect(m_mediaPlayer, &QMediaPlayer::mediaStatusChanged,
            this, &MediaHandler::onMediaStatusChanged);
}

MediaHandler::~MediaHandler()
{
    if (m_mediaPlayer) {
        m_mediaPlayer->stop();
    }
    // Do NOT manually delete m_videoWidget!
    // Qt will delete it when its parent is deleted.
    // Just set the pointer to nullptr here for clarity.
    m_videoWidget = nullptr;
}

void MediaHandler::displayImage(const QString &imagePath, QLabel *imageLabel, int maxWidth)
{
    if (!imageLabel) return;
    QString resolvedPath = resolveMediaPath(imagePath, m_baseMediaDir);
    if (!fileExists(resolvedPath)) {
        imageLabel->setText(QString("Image not found:\n%1").arg(imagePath));
        imageLabel->setStyleSheet("color: red; border: 1px solid red; padding: 10px;");
        return;
    }
    QPixmap pixmap(resolvedPath);
    if (pixmap.isNull()) {
        imageLabel->setText(QString("Failed to load image:\n%1").arg(imagePath));
        imageLabel->setStyleSheet("color: red; border: 1px solid red; padding: 10px;");
        return;
    }
    if (pixmap.width() > maxWidth) {
        pixmap = pixmap.scaledToWidth(maxWidth, Qt::SmoothTransformation);
    }
    imageLabel->setPixmap(pixmap);
    imageLabel->setScaledContents(false);
    imageLabel->setAlignment(Qt::AlignCenter);
    imageLabel->setCursor(Qt::PointingHandCursor);
    imageLabel->setToolTip("Click to view full size");
    imageLabel->setProperty("imagePath", resolvedPath);
    imageLabel->installEventFilter(this);
}

void MediaHandler::addMediaButtons(const QJsonObject &media, QWidget *parent, const QString &mediaDir)
{
    if (!parent || media.isEmpty()) return;
    m_baseMediaDir = mediaDir;
    QVBoxLayout *layout = qobject_cast<QVBoxLayout*>(parent->layout());
    if (!layout) {
        layout = new QVBoxLayout(parent);
    }
    if (media.contains("audio")) {
        QString audioPath = media["audio"].toString();
        embedAudioPlayer(audioPath, parent);
    }

    if (media.contains("video")) {
        QString videoPath = media["video"].toString();
        embedVideoPlayer(videoPath, parent, s_videoWidth, s_videoHeight);
    }

    if (media.contains("image")) {
        QString imagePath = media["image"].toString();
        QLabel *imageLabel = new QLabel(parent);
        displayImage(imagePath, imageLabel, DEFAULT_IMAGE_WIDTH);
        layout->addWidget(imageLabel);
    }
}

void MediaHandler::showFullImage(const QString &imagePath, QWidget *parent)
{
    createImagePreviewDialog(imagePath, parent);
}

void MediaHandler::playAudio(const QString &audioPath)
{
    if (!m_mediaPlayer) return;
    QString resolvedPath = resolveMediaPath(audioPath, m_baseMediaDir);
    if (!fileExists(resolvedPath)) {
        QMessageBox::warning(nullptr, "Audio Error",
                             QString("Audio file not found:\n%1").arg(audioPath));
        return;
    }
    m_mediaPlayer->stop();
    m_mediaPlayer->setSource(QUrl::fromLocalFile(resolvedPath));
    m_audioOutput->setVolume(0.7f);
    m_mediaPlayer->play();
    m_currentAudioPath = resolvedPath;
}

void MediaHandler::playVideo(const QString &videoPath)
{
    QString resolvedPath = resolveMediaPath(videoPath, m_baseMediaDir);
    if (!fileExists(resolvedPath)) {
        QMessageBox::warning(nullptr, "Video Error",
                             QString("Video file not found:\n%1").arg(videoPath));
        return;
    }
    #ifdef Q_OS_LINUX
    QStringList players = {"vlc", "mpv", "mplayer", "totem", "dragon"};
    for (const QString &player : players) {
        if (QStandardPaths::findExecutable(player).isEmpty()) continue;
        QProcess *process = new QProcess(this);
        process->start(player, {resolvedPath});
        if (process->waitForStarted(3000)) return;
    }
    #elif defined(Q_OS_MACOS)
    QProcess::startDetached("open", {resolvedPath});
    #elif defined(Q_OS_WINDOWS)
    QProcess::startDetached("cmd", {"/c", "start", resolvedPath});
    #endif
    QMessageBox::information(nullptr, "Video Player",
                             QString("Please open the video file manually:\n%1").arg(resolvedPath));
}

void MediaHandler::stopMedia()
{
    if (m_mediaPlayer) m_mediaPlayer->stop();
}

QString MediaHandler::resolveMediaPath(const QString &path, const QString &baseDir)
{
    if (QFileInfo(path).isAbsolute()) return path;
    if (!baseDir.isEmpty()) {
        return QDir(baseDir).absoluteFilePath(path);
    }
    return path;
}

bool MediaHandler::fileExists(const QString &path)
{
    return QFileInfo::exists(path) && QFileInfo(path).isFile();
}

void MediaHandler::onPlayAudioClicked()
{
    if (auto button = qobject_cast<QPushButton*>(sender())) {
        playAudio(button->property("audioPath").toString());
    }
}

void MediaHandler::onPlayVideoClicked()
{
    if (auto button = qobject_cast<QPushButton*>(sender())) {
        playVideo(button->property("videoPath").toString());
    }
}

void MediaHandler::onMediaPlayerError()
{
    if (m_mediaPlayer) {
        QMessageBox::warning(nullptr, "Media Player Error",
                             QString("Media playback error:\n%1").arg(m_mediaPlayer->errorString()));
    }
}

void MediaHandler::onMediaStatusChanged()
{
    // Optional: handle status changes
    if (m_mediaPlayer && m_mediaPlayer->mediaStatus() == QMediaPlayer::InvalidMedia) {
        QMessageBox::warning(nullptr, "Media Error", "Invalid media file");
    }
}

// -------- AUDIO PLAYER --------
void MediaHandler::embedAudioPlayer(const QString &audioPath, QWidget *parent)
{
    QString resolvedPath = resolveMediaPath(audioPath, m_baseMediaDir);
    if (!fileExists(resolvedPath)) {
        QMessageBox::warning(nullptr, "Audio Error", QString("Audio file not found:\n%1").arg(audioPath));
        return;
    }

    m_mediaPlayer->stop();
    m_mediaPlayer->setSource(QUrl::fromLocalFile(resolvedPath));

    // Build UI container
    QWidget *container = new QWidget(parent);
    QHBoxLayout *layout = new QHBoxLayout(container);

    QPushButton *playBtn = new QPushButton("▶", container);
    QPushButton *pauseBtn = new QPushButton("⏸", container);

    QSlider *seekBar = new QSlider(Qt::Horizontal, container);
    seekBar->setRange(0, 0);

    QSlider *volumeSlider = new QSlider(Qt::Horizontal, container);
    volumeSlider->setRange(0, 100);
    volumeSlider->setValue(int(m_audioOutput->volume() * 100));
    QLabel *volLabel = new QLabel("Vol:", container);

    layout->addWidget(playBtn);
    layout->addWidget(pauseBtn);
    layout->addWidget(new QLabel("Seek:", container));
    layout->addWidget(seekBar, 12);
    layout->addWidget(volLabel);
    layout->addWidget(volumeSlider, 3);

    // Playback + seek connections
    connect(playBtn, &QPushButton::clicked, m_mediaPlayer, &QMediaPlayer::play);
    connect(pauseBtn, &QPushButton::clicked, m_mediaPlayer, &QMediaPlayer::pause);
    connect(volumeSlider, &QSlider::valueChanged, [this](int v) {
        m_audioOutput->setVolume(v / 100.0f);
    });

    // Fix seeking: update and force-enable on media status change (macOS/Qt6 fix)
    connect(m_mediaPlayer, &QMediaPlayer::mediaStatusChanged, seekBar, [seekBar, this]() {
        seekBar->setMaximum(m_mediaPlayer->duration());
        seekBar->setEnabled(m_mediaPlayer->duration() > 0);
        seekBar->setValue(m_mediaPlayer->position());
    });

    connect(m_mediaPlayer, &QMediaPlayer::durationChanged, seekBar, &QSlider::setMaximum);
    connect(m_mediaPlayer, &QMediaPlayer::positionChanged, seekBar, &QSlider::setValue);
    connect(seekBar, &QSlider::sliderMoved, m_mediaPlayer, &QMediaPlayer::setPosition);

    // Attach to parent layout
    QVBoxLayout *parentLayout = qobject_cast<QVBoxLayout *>(parent->layout());
    if (!parentLayout)
        parentLayout = new QVBoxLayout(parent);
    parentLayout->addWidget(container);

    container->show();
    container->update();
}


// -------- VIDEO PLAYER --------
void MediaHandler::embedVideoPlayer(const QString &videoPath, QWidget *parent, int width, int height)
{
    QString resolvedPath = resolveMediaPath(videoPath, m_baseMediaDir);
    if (!fileExists(resolvedPath)) {
        QMessageBox::warning(nullptr, "Video Error", QString("Video file not found:\n%1").arg(videoPath));
        return;
    }

    // Delete previous video widget container if any
    if (m_videoWidget) {
        m_videoWidget = nullptr;
    }

    // Create container for video UI
    QWidget *container = new QWidget(parent);
    QVBoxLayout *layout = new QVBoxLayout(container);

#ifdef Q_OS_MAC
    QVideoWidget *videoWidget = new QVideoWidget(container);
    videoWidget->setMinimumSize(width, height);
    videoWidget->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Expanding);
    layout->addWidget(videoWidget, 15);
    m_mediaPlayer->setVideoOutput(videoWidget);
#else
    QGraphicsView *graphicsView = new QGraphicsView(container);
    QGraphicsScene *scene = new QGraphicsScene(graphicsView);
    QGraphicsVideoItem *videoItem = new QGraphicsVideoItem();
    scene->addItem(videoItem);
    videoItem->setSize(QSizeF(width, height));
    graphicsView->setScene(scene);
    graphicsView->setMinimumSize(width, height);
    graphicsView->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Expanding);
    layout->addWidget(graphicsView, 15);
    m_mediaPlayer->setVideoOutput(videoItem);
#endif

    // Playback controls layout
    QHBoxLayout *controls = new QHBoxLayout();

    QPushButton *playBtn = new QPushButton("▶", container);
    QPushButton *pauseBtn = new QPushButton("⏸", container);
    QSlider *seekBar = new QSlider(Qt::Horizontal, container);
    seekBar->setRange(0, 0);

    QSlider *volumeSlider = new QSlider(Qt::Horizontal, container);
    volumeSlider->setRange(0, 100);
    volumeSlider->setValue(int(m_audioOutput->volume() * 100));
    QLabel *volLabel = new QLabel("Vol:", container);

    controls->addWidget(playBtn);
    controls->addWidget(pauseBtn);
    controls->addWidget(new QLabel("Seek:", container));
    controls->addWidget(seekBar, 12);
    controls->addWidget(volLabel);
    controls->addWidget(volumeSlider, 3);

    connect(playBtn, &QPushButton::clicked, m_mediaPlayer, &QMediaPlayer::play);
    connect(pauseBtn, &QPushButton::clicked, m_mediaPlayer, &QMediaPlayer::pause);
    connect(volumeSlider, &QSlider::valueChanged, [this](int value){ m_audioOutput->setVolume(value / 100.0f); });

    connect(m_mediaPlayer, &QMediaPlayer::mediaStatusChanged, seekBar, [seekBar, this]() {
        seekBar->setMaximum(m_mediaPlayer->duration());
        seekBar->setEnabled(m_mediaPlayer->duration() > 0);
        seekBar->setValue(m_mediaPlayer->position());
    });

    connect(m_mediaPlayer, &QMediaPlayer::durationChanged, seekBar, &QSlider::setMaximum);
    connect(m_mediaPlayer, &QMediaPlayer::positionChanged, seekBar, &QSlider::setValue);
    connect(seekBar, &QSlider::sliderMoved, m_mediaPlayer, &QMediaPlayer::setPosition);

    layout->addLayout(controls, 1);

    m_mediaPlayer->setSource(QUrl::fromLocalFile(resolvedPath));

    QVBoxLayout *parentLayout = qobject_cast<QVBoxLayout *>(parent->layout());
    if (!parentLayout) parentLayout = new QVBoxLayout(parent);
    parentLayout->addWidget(container);
    container->show();
    container->update();

    m_videoWidget = container;

    QPushButton *fullscreenBtn = new QPushButton("⛶ Fullscreen", container);
    controls->addWidget(fullscreenBtn);

    connect(fullscreenBtn, &QPushButton::clicked, container, [=]() {
#ifdef Q_OS_MAC
        QDialog *dialog = new QDialog(container);
        dialog->setWindowTitle("Fullscreen Video");
        dialog->setWindowFlags(Qt::Window | Qt::FramelessWindowHint);
        dialog->setAttribute(Qt::WA_DeleteOnClose);
        QVBoxLayout *vbox = new QVBoxLayout(dialog);
        QVideoWidget *fsVideoWidget = new QVideoWidget(dialog);
        fsVideoWidget->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Expanding);
        vbox->addWidget(fsVideoWidget);
        m_mediaPlayer->setVideoOutput(fsVideoWidget);
        dialog->showFullScreen();

        connect(dialog, &QDialog::finished, container, [=]() {
            m_mediaPlayer->setVideoOutput(videoWidget);
        });
#else
        // Non-Mac fullscreen logic: show video in fullscreen QGraphicsView
        QDialog *dialog = new QDialog(container);
        dialog->setWindowTitle("Fullscreen Video");
        dialog->setWindowFlags(Qt::Window | Qt::FramelessWindowHint);
        dialog->setAttribute(Qt::WA_DeleteOnClose);

        QScreen *screen = QApplication::primaryScreen();
        QRect screenRect = screen->geometry();
        dialog->resize(screenRect.size());

        QVBoxLayout *vbox = new QVBoxLayout(dialog);
        vbox->setContentsMargins(0, 0, 0, 0);

        QGraphicsView *fsView = new QGraphicsView(dialog);
        fsView->setHorizontalScrollBarPolicy(Qt::ScrollBarAlwaysOff);
        fsView->setVerticalScrollBarPolicy(Qt::ScrollBarAlwaysOff);
        fsView->setFrameShape(QFrame::NoFrame);

        QGraphicsScene *fsScene = new QGraphicsScene(fsView);
        QGraphicsVideoItem *fsVideoItem = new QGraphicsVideoItem();
        fsScene->addItem(fsVideoItem);
        fsView->setScene(fsScene);
        fsView->setAlignment(Qt::AlignCenter);
        fsView->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Expanding);

        vbox->addWidget(fsView);

        // Set new video output
        m_mediaPlayer->setVideoOutput(fsVideoItem);

        // Sync size when resized
        struct ResizeSync : public QObject {
            QGraphicsVideoItem *item;
            QGraphicsView *view;
            ResizeSync(QGraphicsVideoItem *i, QGraphicsView *v) : item(i), view(v) {}
            bool eventFilter(QObject *obj, QEvent *event) override {
                if (event->type() == QEvent::Resize && obj == view->viewport()) {
                    item->setSize(QSizeF(view->viewport()->size()));
                }
                return QObject::eventFilter(obj, event);
            }
        };

        auto resizeSync = new ResizeSync(fsVideoItem, fsView);
        fsView->viewport()->installEventFilter(resizeSync);
        fsVideoItem->setSize(QSizeF(fsView->viewport()->size()));

        dialog->showFullScreen();

        // Restore to original video output on close
        connect(dialog, &QDialog::finished, container, [=]() {
            m_mediaPlayer->setVideoOutput(videoItem);
            resizeSync->deleteLater();
        });

        // Escape key closes fullscreen dialog
        dialog->installEventFilter(container);
        container->setProperty("fullscreen_dialog", QVariant::fromValue(dialog));
#endif
    });
}

void MediaHandler::createImagePreviewDialog(const QString &imagePath, QWidget *parent)
{
    QDialog *dialog = new QDialog(parent);
    dialog->setWindowTitle("Image Preview");
    dialog->setModal(false);
    dialog->setAttribute(Qt::WA_DeleteOnClose);

    QPixmap pixmap(imagePath);
    if (pixmap.isNull()) {
        QMessageBox::warning(parent, "Error",
            QString("Failed to load image:\n%1").arg(imagePath));
        delete dialog;
        return;
    }

    QScrollArea *scrollArea = new QScrollArea(dialog);
    scrollArea->setBackgroundRole(QPalette::Dark);
    scrollArea->setAlignment(Qt::AlignCenter);

    QLabel *imageLabel = new QLabel;
    imageLabel->setPixmap(pixmap);
    imageLabel->setScaledContents(false); // WE DO NOT want DSTRETCH
    scrollArea->setWidget(imageLabel);

    QVBoxLayout *layout = new QVBoxLayout(dialog);
    layout->addWidget(scrollArea);

    bool *scaledMode = new bool(true); // true = scaled-to-window, false = 1:1

    // Helper to show the pixmap at the right size/aspect.
    auto fitLabelToViewport = [=]() {
        if (*scaledMode) {
            QSize avail = scrollArea->viewport()->size();
            if (avail.width() > 2 && avail.height() > 2) {
                QPixmap scaled = pixmap.scaled(avail, Qt::KeepAspectRatio, Qt::SmoothTransformation);
                imageLabel->setPixmap(scaled);
                imageLabel->resize(scaled.size());
            }
        } else {
            imageLabel->setPixmap(pixmap);
            imageLabel->resize(pixmap.size());
        }
    };

    // Event filter for resizing (scrollArea viewport)
    class ViewportResizeFilter : public QObject {
        std::function<void()> updateFn;
    public:
        ViewportResizeFilter(std::function<void()> fn, QObject *parent = nullptr)
            : QObject(parent), updateFn(fn) {}
        bool eventFilter(QObject *, QEvent *event) override {
            if (event->type() == QEvent::Resize) {
                updateFn();
            }
            return false;
        }
    };
    scrollArea->viewport()->installEventFilter(new ViewportResizeFilter(fitLabelToViewport, scrollArea->viewport()));

    // Toggle mode on image click
    class ToggleFilter : public QObject {
        std::function<void()> updateFn;
        bool *mode;
    public:
        ToggleFilter(std::function<void()> fn, bool *m, QObject *parent=nullptr)
            : QObject(parent), updateFn(fn), mode(m) {}
        bool eventFilter(QObject *, QEvent *event) override {
            if (event->type() == QEvent::MouseButtonRelease) {
                *mode = !*mode;
                updateFn();
                return true;
            }
            return false;
        }
    };
    imageLabel->setCursor(Qt::PointingHandCursor);
    imageLabel->installEventFilter(new ToggleFilter(fitLabelToViewport, scaledMode, imageLabel));

    // Initial sizing
    QSize screen = QApplication::primaryScreen()->availableGeometry().size();
    int maxW = qMin(pixmap.width() + 50, int(screen.width() * 0.9));
    int maxH = qMin(pixmap.height() + 50, int(screen.height() * 0.9));
    dialog->resize(maxW, maxH);
    fitLabelToViewport();

    dialog->show();
    dialog->raise();
    dialog->activateWindow();
}



bool MediaHandler::eventFilter(QObject *object, QEvent *event)
{
    if (QLabel *label = qobject_cast<QLabel*>(object)) {
        if (event->type() == QEvent::MouseButtonPress) {
            if (auto *mouseEvent = static_cast<QMouseEvent*>(event); mouseEvent->button() == Qt::LeftButton) {
                QString imagePath = label->property("imagePath").toString();
                if (!imagePath.isEmpty()) {
                    showFullImage(imagePath, label->parentWidget());
                    return true;
                }
            }
        }
    }
    if (QDialog *dialog = qobject_cast<QDialog*>(object)) {
        if (event->type() == QEvent::KeyPress) {
            if (auto *keyEvent = static_cast<QKeyEvent*>(event); keyEvent->key() == Qt::Key_Escape) {
                dialog->close();
                return true;
            }
        }
    }
    return QObject::eventFilter(object, event);
}

