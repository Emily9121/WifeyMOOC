#include "droptag.h"
#include <QApplication>
#include <QMouseEvent>
#include <QPainter>
#include <QMimeData>
#include <QDrag>
#include <QCursor>

// DropTag implementation
DropTag::DropTag(const QString &tagId, const QString &label, const QPoint &initialPos, QWidget *parent)
    : QWidget(parent)
    , m_tagId(tagId)
    , m_label(label)
    , m_isDragging(false)
    , m_dragStartPos(initialPos)
    , m_lastPos(initialPos)
    , m_font("Arial", 12, QFont::Bold)
    , m_backgroundColor(Qt::black)
    , m_textColor(Qt::yellow)
    , m_borderColor(Qt::yellow)
{
    setAcceptDrops(true);
    calculateSize();
    setPosition(initialPos);
    setToolTip(QString("Drag to position: %1").arg(m_label));
    setCursor(Qt::OpenHandCursor);
}

QPoint DropTag::currentPosition() const
{
    return pos();
}

void DropTag::setPosition(const QPoint &pos)
{
    move(pos);
    m_lastPos = pos;
}

QSize DropTag::sizeHint() const
{
    return m_textSize + QSize(2 * PADDING_X, 2 * PADDING_Y);
}

QSize DropTag::minimumSizeHint() const
{
    return sizeHint();
}

void DropTag::calculateSize()
{
    QFontMetrics metrics(m_font);
    m_textSize = metrics.size(Qt::TextSingleLine, m_label);
    setFixedSize(sizeHint());
}

void DropTag::updateGeometry()
{
    calculateSize();
    update();
}

void DropTag::paintEvent(QPaintEvent *event)
{
    Q_UNUSED(event)
    
    QPainter painter(this);
    painter.setRenderHint(QPainter::Antialiasing);
    
    QRect rect = this->rect().adjusted(BORDER_WIDTH/2, BORDER_WIDTH/2, 
                                      -BORDER_WIDTH/2, -BORDER_WIDTH/2);
    
    // Draw background
    painter.fillRect(rect, m_backgroundColor);
    
    // Draw border
    painter.setPen(QPen(m_borderColor, BORDER_WIDTH));
    painter.drawRect(rect);
    
    // Draw text
    painter.setPen(m_textColor);
    painter.setFont(m_font);
    painter.drawText(rect, Qt::AlignCenter, m_label);
}

void DropTag::mousePressEvent(QMouseEvent *event)
{
    if (event->button() == Qt::LeftButton) {
        m_isDragging = false;
        m_dragStartPos = event->pos();
        setCursor(Qt::ClosedHandCursor);
        emit tagSelected(m_tagId);
    }
    QWidget::mousePressEvent(event);
}

void DropTag::mouseMoveEvent(QMouseEvent *event)
{
    if (!(event->buttons() & Qt::LeftButton)) {
        return;
    }
    
    if (!m_isDragging) {
        int distance = (event->pos() - m_dragStartPos).manhattanLength();
        if (distance >= QApplication::startDragDistance()) {
            m_isDragging = true;
        } else {
            return;
        }
    }
    
    // Move the widget
    QPoint newPos = pos() + event->pos() - m_dragStartPos;
    
    // Constrain to parent bounds if parent exists
    if (parentWidget()) {
        QRect parentRect = parentWidget()->rect();
        newPos.setX(qMax(0, qMin(newPos.x(), parentRect.width() - width())));
        newPos.setY(qMax(0, qMin(newPos.y(), parentRect.height() - height())));
    }
    
    move(newPos);
    m_lastPos = newPos;
    
    emit tagMoved(m_tagId, newPos);
    
    QWidget::mouseMoveEvent(event);
}

void DropTag::mouseReleaseEvent(QMouseEvent *event)
{
    if (event->button() == Qt::LeftButton) {
        m_isDragging = false;
        setCursor(Qt::OpenHandCursor);
        
        if (m_lastPos != pos()) {
            emit tagMoved(m_tagId, pos());
        }
    }
    QWidget::mouseReleaseEvent(event);
}

void DropTag::dragEnterEvent(QDragEnterEvent *event)
{
    if (event->mimeData()->hasFormat("application/x-droptag")) {
        event->acceptProposedAction();
    }
}

void DropTag::dragMoveEvent(QDragMoveEvent *event)
{
    if (event->mimeData()->hasFormat("application/x-droptag")) {
        event->acceptProposedAction();
    }
}

void DropTag::dropEvent(QDropEvent *event)
{
    if (event->mimeData()->hasFormat("application/x-droptag")) {
        event->acceptProposedAction();
    }
}

// ImageTaggingWidget implementation
ImageTaggingWidget::ImageTaggingWidget(QWidget *parent)
    : QWidget(parent)
    , m_scaleFactor(1.0)
    , m_imageOffset(0, 0)
{
    setAcceptDrops(true);
    setMinimumSize(400, 300);
    setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Expanding);
}

void ImageTaggingWidget::setBackgroundImage(const QString &imagePath)
{
    m_backgroundImagePath = imagePath;
    m_backgroundPixmap = QPixmap(imagePath);
    
    if (!m_backgroundPixmap.isNull()) {
        m_imageSize = m_backgroundPixmap.size();
        setMinimumSize(m_imageSize);
        updateTagPositions();
        update();
    }
}

void ImageTaggingWidget::addTag(const QString &tagId, const QString &label, const QPoint &position)
{
    if (m_tags.contains(tagId)) {
        // Update existing tag
        DropTag *tag = m_tags[tagId];
        tag->setPosition(position);
        return;
    }
    
    DropTag *tag = new DropTag(tagId, label, position, this);
    
    connect(tag, &DropTag::tagMoved, this, &ImageTaggingWidget::onTagMoved);
    connect(tag, &DropTag::tagSelected, this, &ImageTaggingWidget::onTagSelected);
    
    m_tags[tagId] = tag;
    tag->show();
    tag->raise();
}

void ImageTaggingWidget::clearTags()
{
    for (auto it = m_tags.begin(); it != m_tags.end(); ++it) {
        it.value()->deleteLater();
    }
    m_tags.clear();
}

QPoint ImageTaggingWidget::getTagPosition(const QString &tagId) const
{
    if (m_tags.contains(tagId)) {
        return m_tags[tagId]->currentPosition();
    }
    return QPoint(-1, -1);
}

void ImageTaggingWidget::setTagPosition(const QString &tagId, const QPoint &pos)
{
    if (m_tags.contains(tagId)) {
        m_tags[tagId]->setPosition(pos);
    }
}

QStringList ImageTaggingWidget::getAllTagIds() const
{
    return m_tags.keys();
}

void ImageTaggingWidget::paintEvent(QPaintEvent *event)
{
    Q_UNUSED(event)
    
    QPainter painter(this);
    painter.setRenderHint(QPainter::Antialiasing);
    
    if (!m_backgroundPixmap.isNull()) {
        // Calculate scaling and offset to center the image
        QSize widgetSize = size();
        QSize imageSize = m_backgroundPixmap.size();
        
        m_scaleFactor = qMin(
            double(widgetSize.width()) / imageSize.width(),
            double(widgetSize.height()) / imageSize.height()
        );
        
        QSize scaledSize = imageSize * m_scaleFactor;
        m_imageOffset = QPoint(
            (widgetSize.width() - scaledSize.width()) / 2,
            (widgetSize.height() - scaledSize.height()) / 2
        );
        
        QRect drawRect(m_imageOffset, scaledSize);
        painter.drawPixmap(drawRect, m_backgroundPixmap);
    } else {
        // Draw placeholder
        painter.fillRect(rect(), Qt::lightGray);
        painter.setPen(Qt::darkGray);
        painter.drawText(rect(), Qt::AlignCenter, "No Image Loaded");
    }
}

void ImageTaggingWidget::resizeEvent(QResizeEvent *event)
{
    QWidget::resizeEvent(event);
    updateTagPositions();
}

void ImageTaggingWidget::dragEnterEvent(QDragEnterEvent *event)
{
    if (event->mimeData()->hasFormat("application/x-droptag")) {
        event->acceptProposedAction();
    }
}

void ImageTaggingWidget::dragMoveEvent(QDragMoveEvent *event)
{
    if (event->mimeData()->hasFormat("application/x-droptag")) {
        event->acceptProposedAction();
    }
}

void ImageTaggingWidget::dropEvent(QDropEvent *event)
{
    if (event->mimeData()->hasFormat("application/x-droptag")) {
        QByteArray data = event->mimeData()->data("application/x-droptag");
        QString tagId = QString::fromUtf8(data);
        
        if (m_tags.contains(tagId)) {
            QPoint dropPos = event->position().toPoint();
            m_tags[tagId]->setPosition(dropPos);
            emit tagPositionChanged(tagId, dropPos);
        }
        
        event->acceptProposedAction();
    }
}

void ImageTaggingWidget::onTagMoved(const QString &tagId, const QPoint &newPos)
{
    emit tagPositionChanged(tagId, newPos);
}

void ImageTaggingWidget::onTagSelected(const QString &tagId)
{
    emit tagSelected(tagId);
    
    // Bring selected tag to front
    if (m_tags.contains(tagId)) {
        m_tags[tagId]->raise();
    }
}

void ImageTaggingWidget::updateTagPositions()
{
    // Scale tag positions based on current widget size vs image size
    if (m_backgroundPixmap.isNull()) return;
    
    for (auto it = m_tags.begin(); it != m_tags.end(); ++it) {
        DropTag *tag = it.value();
        QPoint currentPos = tag->currentPosition();
        
        // Apply scaling and offset if needed
        // This could be enhanced to maintain relative positions when resizing
        tag->setPosition(currentPos);
    }
}

QPointF ImageTaggingWidget::tagPositionInImage(const QString &tagId) const
{
    if (!m_tags.contains(tagId) || m_backgroundPixmap.isNull())
        return QPointF(-1, -1);
    // DropTag position in widget space:
    QPoint widgetPos = m_tags[tagId]->currentPosition();
    // Convert to natural image coordinates (undo offset and scaling):
    return (widgetPos - m_imageOffset) / m_scaleFactor;
}

void ImageTaggingWidget::setTagPositionInImage(const QString &tagId, const QPointF &imgPt)
{
    if (!m_tags.contains(tagId) || m_backgroundPixmap.isNull())
        return;
    QPoint widgetPt = (imgPt * m_scaleFactor).toPoint() + m_imageOffset;
    m_tags[tagId]->setPosition(widgetPt);
}