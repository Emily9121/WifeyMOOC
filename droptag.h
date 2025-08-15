#ifndef DROPTAG_H
#define DROPTAG_H

#include <QWidget>
#include <QLabel>
#include <QMouseEvent>
#include <QPaintEvent>
#include <QDragEnterEvent>
#include <QDragMoveEvent>
#include <QDropEvent>
#include <QPainter>
#include <QMimeData>
#include <QDrag>
#include <QPixmap>
#include <QPoint>
#include <QSize>
#include <QFont>
#include <QFontMetrics>
#include <QColor>
#include <QPen>
#include <QBrush>

class DropTag : public QWidget
{
    Q_OBJECT

public:
    explicit DropTag(const QString &tagId, 
                     const QString &label, 
                     const QPoint &initialPos,
                     QWidget *parent = nullptr);
    
    QString tagId() const { return m_tagId; }
    QString label() const { return m_label; }
    QPoint currentPosition() const;
    void setPosition(const QPoint &pos);
    
    // Size management
    QSize sizeHint() const override;
    QSize minimumSizeHint() const override;

protected:
    void paintEvent(QPaintEvent *event) override;
    void mousePressEvent(QMouseEvent *event) override;
    void mouseMoveEvent(QMouseEvent *event) override;
    void mouseReleaseEvent(QMouseEvent *event) override;
    
    void dragEnterEvent(QDragEnterEvent *event) override;
    void dragMoveEvent(QDragMoveEvent *event) override;
    void dropEvent(QDropEvent *event) override;

signals:
    void tagMoved(const QString &tagId, const QPoint &newPos);
    void tagSelected(const QString &tagId);

private:
    void calculateSize();
    void updateGeometry();
    
    QString m_tagId;
    QString m_label;
    
    // Dragging state
    bool m_isDragging;
    QPoint m_dragStartPos;
    QPoint m_lastPos;
    
    // Appearance
    QFont m_font;
    QSize m_textSize;
    QColor m_backgroundColor;
    QColor m_textColor;
    QColor m_borderColor;
    
    // Layout constants
    static constexpr int PADDING_X = 6;
    static constexpr int PADDING_Y = 3;
    static constexpr int BORDER_WIDTH = 2;
};

// Custom widget for holding draggable tags over an image
class ImageTaggingWidget : public QWidget
{
    Q_OBJECT

public:
    explicit ImageTaggingWidget(QWidget *parent = nullptr);
    
    void setBackgroundImage(const QString &imagePath);
    void addTag(const QString &tagId, const QString &label, const QPoint &position);
    void clearTags();
    
    // Tag management
    QPoint getTagPosition(const QString &tagId) const;
    void setTagPosition(const QString &tagId, const QPoint &pos);
    QStringList getAllTagIds() const;
    
    // Image management
    QString backgroundImagePath() const { return m_backgroundImagePath; }
    QSize imageSize() const { return m_imageSize; }

    // Scalling
    QPointF tagPositionInImage(const QString &tagId) const;
    void setTagPositionInImage(const QString &tagId, const QPointF &imgPt);
    
protected:
    void paintEvent(QPaintEvent *event) override;
    void resizeEvent(QResizeEvent *event) override;
    void dragEnterEvent(QDragEnterEvent *event) override;
    void dragMoveEvent(QDragMoveEvent *event) override;
    void dropEvent(QDropEvent *event) override;

private slots:
    void onTagMoved(const QString &tagId, const QPoint &newPos);
    void onTagSelected(const QString &tagId);

signals:
    void tagPositionChanged(const QString &tagId, const QPoint &newPos);
    void tagSelected(const QString &tagId);

private:
    void updateTagPositions();
    
    QString m_backgroundImagePath;
    QPixmap m_backgroundPixmap;
    QSize m_imageSize;
    QMap<QString, DropTag*> m_tags;
    
    // Scaling for display
    double m_scaleFactor;
    QPoint m_imageOffset;
};

#endif // DROPTAG_H