#include "questionhandlers.h"
#include "mediahandler.h"
#include "droptag.h"

#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QGridLayout>
#include <QLabel>
#include <QRadioButton>
#include <QButtonGroup>
#include <QCheckBox>
#include <QListWidget>
#include <QComboBox>
#include <QLineEdit>
#include <QPushButton>
#include <QSpinBox>
#include <QPixmap>
#include <QFileInfo>
#include <QDir>
#include <QToolButton>
#include <QIcon>
#include <QDebug>

#define DEBUG_IMAGE_TAGGING 1

QuestionHandlers::QuestionHandlers(QObject *parent)
    : QObject(parent),
      m_currentQuestionWidget(nullptr),
      m_mediaHandler(nullptr),
      m_mcqButtonGroup(nullptr),
      m_listPickWidget(nullptr),
      m_categorizationCombo(nullptr),
      m_imageTaggingWidget(nullptr),
      m_imageLabel(nullptr),
      m_imageTaggingAltIndex(0),
      m_lastFocusedEntry(nullptr)
{}

void QuestionHandlers::clearCurrentQuestion() {
    m_currentQuestionWidget = nullptr;
    m_currentQuestion = QJsonObject();
    m_currentQuestionType.clear();

    m_buttonGroups.clear();
    m_mcqButtonGroup = nullptr;
    m_mcqCheckBoxes.clear();
    m_wordFillEntries.clear();
    m_listPickWidget = nullptr;
    m_matchComboBoxes.clear();
    m_categorizationCombo = nullptr;
    m_multipleCategorizationCombosMap.clear(); // Corrected variable name!
    m_sequenceSpinBoxes.clear();
    m_orderPhraseWords.clear();
    m_orderPhraseLabels.clear();
    m_fillBlanksDropdowns.clear();
    m_matchPhraseCombos.clear();
    m_imageTaggingWidget = nullptr;
    m_dropTags.clear();
    m_imageLabel = nullptr;
    m_imageTaggingAlternatives = QJsonArray();
    m_multipleCategorizationCombosMap.clear();
}

QWidget* QuestionHandlers::createQuestionWidget(const QJsonObject &question,
    QWidget *parent,
    const QString &mediaDir,
    MediaHandler *mediaHandler,
    int imageTaggingAltIndex,
    const QString &questionKey)
{
    // The original clear was too aggressive for multi-question! We only clear for top-level questions.
    if (!questionKey.contains('-')) {
        clearCurrentQuestion();
    }
    m_currentQuestion = question;
    m_currentQuestionWidget = parent;
    m_mediaDir = mediaDir;
    m_mediaHandler = mediaHandler;
    m_currentQuestionType = question["type"].toString();
    m_imageTaggingAltIndex = imageTaggingAltIndex;
    m_currentQuestionKey = questionKey;

    if (question.contains("media"))
        mediaHandler->addMediaButtons(question["media"].toObject(), parent, mediaDir);

    if (m_currentQuestionType == "mcq_single") return createMcqSingle(question, parent);
    if (m_currentQuestionType == "mcq_multiple") return createMcqMultiple(question, parent);
    if (m_currentQuestionType == "word_fill") return createWordFill(question, parent);
    if (m_currentQuestionType == "list_pick") return createListPick(question, parent);
    if (m_currentQuestionType == "match_sentence") return createMatchSentence(question, parent);
    if (m_currentQuestionType == "categorization") return createCategorization(question, parent);
    if (m_currentQuestionType == "categorization_multiple") return createCategorizationMultiple(question, parent);
    if (m_currentQuestionType == "sequence_audio") return createSequenceAudio(question, parent);
    if (m_currentQuestionType == "order_phrase") return createOrderPhrase(question, parent);
    if (m_currentQuestionType == "fill_blanks_dropdown") return createFillBlanksDropdown(question, parent);
    if (m_currentQuestionType == "match_phrases") return createMatchPhrases(question, parent);
    if (m_currentQuestionType == "image_tagging") return createImageTagging(question, parent);

    QVBoxLayout *layout = qobject_cast<QVBoxLayout*>(parent->layout());
    if (!layout) layout = new QVBoxLayout(parent);
    layout->addWidget(new QLabel(QString("Unsupported question type: %1").arg(m_currentQuestionType), parent));
    return parent;
}

QWidget* QuestionHandlers::createMcqSingle(const QJsonObject &question, QWidget *parent) {
    QVBoxLayout *layout = qobject_cast<QVBoxLayout*>(parent->layout());
    if (!layout) layout = new QVBoxLayout(parent);

    QJsonArray opts = question["options"].toArray();
    QButtonGroup* buttonGroup = new QButtonGroup(parent);
    buttonGroup->setExclusive(true);

    for (int i = 0; i < opts.size(); ++i) {
        QJsonValue optionVal = opts[i];
        QAbstractButton* button;

        if(optionVal.isObject()) {
            QJsonObject optionObj = optionVal.toObject();
            QToolButton* toolButton = new QToolButton(parent);
            QString imgPath = resolveImagePath(optionObj["image"].toString());
            toolButton->setIcon(QIcon(imgPath));
            toolButton->setIconSize(QSize(128, 128));
            toolButton->setToolButtonStyle(Qt::ToolButtonTextUnderIcon);
            toolButton->setText(optionObj["text"].toString());
            button = toolButton;
        } else {
            button = new QRadioButton(optionVal.toString(), parent);
        }
        button->setCheckable(true);
        buttonGroup->addButton(button, i);
        layout->addWidget(button);
    }
    
    m_buttonGroups[m_currentQuestionKey] = buttonGroup;
    m_mcqButtonGroup = buttonGroup;
    
    connect(buttonGroup, &QButtonGroup::buttonClicked, this, &QuestionHandlers::answerChanged);
    return parent;
}

QWidget* QuestionHandlers::createMcqMultiple(const QJsonObject &question, QWidget *parent) {
    QVBoxLayout *layout = qobject_cast<QVBoxLayout*>(parent->layout());
    if (!layout) layout = new QVBoxLayout(parent);

    QJsonArray opts = question["options"].toArray();
    
    QButtonGroup* buttonGroup = new QButtonGroup(parent);
    buttonGroup->setExclusive(false);

    m_mcqCheckBoxes.clear();
    for (int i=0; i < opts.size(); ++i) {
        QJsonValue optionVal = opts[i];
        QAbstractButton* button;
        
        if(optionVal.isObject()) {
            QJsonObject optionObj = optionVal.toObject();
            QToolButton* toolButton = new QToolButton(parent);
            QString imgPath = resolveImagePath(optionObj["image"].toString());
            toolButton->setIcon(QIcon(imgPath));
            toolButton->setIconSize(QSize(128, 128));
            toolButton->setToolButtonStyle(Qt::ToolButtonTextUnderIcon);
            toolButton->setText(optionObj["text"].toString());
            button = toolButton;
        } else {
            QCheckBox* cb = new QCheckBox(optionVal.toString(), parent);
            m_mcqCheckBoxes.append(cb);
            button = cb;
        }
        
        button->setCheckable(true);
        buttonGroup->addButton(button, i);
        layout->addWidget(button);
        connect(button, &QAbstractButton::clicked, this, &QuestionHandlers::answerChanged);
    }
    m_buttonGroups[m_currentQuestionKey] = buttonGroup;
    return parent;
}

QWidget* QuestionHandlers::createWordFill(const QJsonObject &question, QWidget *parent) {
    QVBoxLayout *vl = qobject_cast<QVBoxLayout*>(parent->layout());
    if (!vl) vl = new QVBoxLayout(parent);

    m_wordFillEntries.clear();
    m_lastFocusedEntry = nullptr; // track last active entry for accents

    // ---- ACCENT BUTTONS ----
    QStringList accentRow1 = {"é", "è", "ê", "ë", "à", "â", "î", "ï", "ô", "û", "ù", "ç", "œ", "æ"};
    QStringList accentRow2 = {"É", "È", "Ê", "Ë", "À", "Â", "Î", "Ï", "Ô", "Û", "Ù", "Ç", "Œ", "Æ"};

    QWidget *accentWidget = new QWidget(parent);
    QVBoxLayout *accentLayout = new QVBoxLayout(accentWidget);
    accentLayout->setContentsMargins(0, 0, 0, 0);

    auto createAccentRow = [&](const QStringList &chars) {
        QWidget *rowWidget = new QWidget(accentWidget);
        QHBoxLayout *rowLayout = new QHBoxLayout(rowWidget);
        rowLayout->setContentsMargins(0, 0, 0, 0);
        for (const QString &ch : chars) {
            QPushButton *btn = new QPushButton(ch, rowWidget);
            btn->setFixedWidth(28);
            btn->setFixedHeight(28);
            btn->setFont(QFont("Arial", 12));
            connect(btn, &QPushButton::clicked, this, [this, ch]() {
                if (m_lastFocusedEntry) {
                    m_lastFocusedEntry->insert(ch);
                }
            });
            rowLayout->addWidget(btn);
        }
        accentLayout->addWidget(rowWidget);
    };

    createAccentRow(accentRow1);
    createAccentRow(accentRow2);
    vl->addWidget(accentWidget);

    // ---- SENTENCE PARTS & ENTRIES ----
    QJsonArray parts = question.contains("sentence_parts")
        ? question["sentence_parts"].toArray()
        : (question.contains("parts") ? question["parts"].toArray() : QJsonArray());
    QJsonArray answers = question.contains("answers")
        ? question["answers"].toArray()
        : QJsonArray();

    int nBlanks = answers.size();

    for (int i = 0; i < nBlanks; ++i) {
        // Preceding text part
        if (i < parts.size()) {
            QString txt = parts[i].toString();
            QStringList lines = txt.split('\n');
            for (const QString &line : lines) {
                QLabel *lbl = new QLabel(line, parent);
                lbl->setWordWrap(true);
                vl->addWidget(lbl);
            }
        }
        // Entry for blank
        QLineEdit *edit = new QLineEdit(parent);
        edit->setFont(QFont("Arial", 14));
        connect(edit, &QLineEdit::textChanged, this, &QuestionHandlers::answerChanged);
        connect(edit, &QLineEdit::selectionChanged, this, [this, edit]() {
            m_lastFocusedEntry = edit;
        });
        m_wordFillEntries.append(edit);
        vl->addWidget(edit);
    }

    // Tail text after last blank
    if (!parts.isEmpty() && (int)parts.size() > nBlanks) {
        QStringList lines = parts.last().toString().split('\n');
        for (const QString &line : lines) {
            QLabel *lbl = new QLabel(line, parent);
            lbl->setWordWrap(true);
            vl->addWidget(lbl);
        }
    }

    return parent;
}


// ---------- LIST PICK ----------
QWidget* QuestionHandlers::createListPick(const QJsonObject &question, QWidget *parent) {
    QVBoxLayout *layout = qobject_cast<QVBoxLayout *>(parent->layout());
    if (!layout) {
        layout = new QVBoxLayout(parent);
        parent->setLayout(layout);
    }

    m_listPickWidget = new QListWidget(parent);
    m_listPickWidget->setSelectionMode(QAbstractItemView::MultiSelection);

    QJsonArray items;
    if (question.contains("options"))
        items = question["options"].toArray();
    else if (question.contains("items"))
        items = question["items"].toArray();

    for (const QJsonValue &val : items) {
        QString text;
        if (val.isString()) {
            text = val.toString();
        } else if (val.isObject()) {
            QJsonObject obj = val.toObject();
            if (obj.contains("text")) {
                text = obj["text"].toString();
            } else if (obj.contains("image")) {
                text = QFileInfo(obj["image"].toString()).fileName();
            }
        }
        if (!text.isEmpty()) {
            m_listPickWidget->addItem(text);
        }
    }

    layout->addWidget(m_listPickWidget);

    connect(m_listPickWidget, &QListWidget::itemSelectionChanged, this, &QuestionHandlers::answerChanged);

    return parent;
}



// ---------- MATCH SENTENCE ----------
QWidget* QuestionHandlers::createMatchSentence(const QJsonObject &question, QWidget *parent) {
    QVBoxLayout *vl = qobject_cast<QVBoxLayout*>(parent->layout());
    if (!vl) vl = new QVBoxLayout(parent);

    QJsonArray pairs = question["pairs"].toArray();
    m_matchComboBoxes.clear();

    for (int i = 0; i < pairs.size(); ++i) {
        QJsonObject pair = pairs[i].toObject();
        QHBoxLayout *hl = new QHBoxLayout;

        // Left-hand display: image if present, otherwise text
        if (pair.contains("image_path") && pair["image_path"].isString() && !pair["image_path"].toString().isEmpty()) {
            QLabel *imgLabel = new QLabel(parent);
            if (m_mediaHandler)
                m_mediaHandler->displayImage(pair["image_path"].toString(), imgLabel, 100);
            else
                imgLabel->setText(pair["image_path"].toString());
            hl->addWidget(imgLabel);
        } else if (pair.contains("sentence")) {
            hl->addWidget(new QLabel(pair["sentence"].toString(), parent));
        } else if (pair.contains("left")) {
            hl->addWidget(new QLabel(pair["left"].toString(), parent));
        }

        // Right-hand combo box (options field or build from all sentence texts)
        QComboBox *combo = new QComboBox(parent);
        if (pair.contains("options") && pair["options"].isArray()) {
            for (const QJsonValue &opt : pair["options"].toArray())
                combo->addItem(opt.toString());
        } else {
            // Fallback: gather all sentence texts as options
            for (const QJsonValue &p : pairs) {
                if (p.toObject().contains("sentence"))
                    combo->addItem(p.toObject()["sentence"].toString());
            }
        }
        m_matchComboBoxes.append(combo);
        hl->addWidget(combo);

        vl->addLayout(hl);
        connect(combo, qOverload<int>(&QComboBox::currentIndexChanged), this, &QuestionHandlers::answerChanged);
    }

    return parent;
}


// ---------- CATEGORIZATION ----------
QWidget* QuestionHandlers::createCategorization(const QJsonObject &question, QWidget *parent) {
    QVBoxLayout *layout = qobject_cast<QVBoxLayout*>(parent->layout());
    if (!layout) layout = new QVBoxLayout(parent);

    QJsonArray categories = question["categories"].toArray();
    m_categorizationCombo = new QComboBox(parent);
    for (auto c : categories)
        m_categorizationCombo->addItem(c.toString());

    layout->addWidget(m_categorizationCombo);
    connect(m_categorizationCombo, qOverload<int>(&QComboBox::currentIndexChanged),
            this, &QuestionHandlers::answerChanged);

    return parent;
}

// ---------- CATEGORIZATION MULTIPLE (FIXED) ----------
QWidget* QuestionHandlers::createCategorizationMultiple(const QJsonObject &question, QWidget *parent) {
    QVBoxLayout *vl = qobject_cast<QVBoxLayout*>(parent->layout());
    if (!vl) vl = new QVBoxLayout(parent);

    QWidget *gridContainer = new QWidget(parent);
    QGridLayout *grid = new QGridLayout(gridContainer);

    QJsonArray entries;
    bool hasStimuli = false;
    if (question.contains("stimuli")) {
        entries = question["stimuli"].toArray();
        hasStimuli = true;
    } else if (question.contains("items")) {
        entries = question["items"].toArray();
    }

    QJsonArray cats = question["categories"].toArray();
    QList<QComboBox*> combos;
    int maxCols = question.contains("max_columns") ? question["max_columns"].toInt() : 6;

    for (int i = 0; i < entries.size(); ++i) {
        QVBoxLayout *cellLayout = new QVBoxLayout;

        if (hasStimuli) {
            QJsonObject stim = entries[i].toObject();

            if (stim.contains("image") && stim["image"].isString() && !stim["image"].toString().isEmpty()) {
                QString imgPath = stim["image"].toString();
                QLabel *imgLabel = new QLabel(gridContainer);
                if (m_mediaHandler)
                    m_mediaHandler->displayImage(resolveImagePath(imgPath), imgLabel, 100);
                else
                    imgLabel->setText(imgPath);
                cellLayout->addWidget(imgLabel);
            }
            else if (stim.contains("text")) {
                cellLayout->addWidget(new QLabel(stim["text"].toString(), gridContainer));
            }
            else if (entries[i].isString()) {
                cellLayout->addWidget(new QLabel(entries[i].toString(), gridContainer));
            }
        } else {
            cellLayout->addWidget(new QLabel(entries[i].toString(), gridContainer));
        }

        QComboBox *cb = new QComboBox(gridContainer);
        for (const QJsonValue &c : cats)
            cb->addItem(c.toString());
        combos.append(cb);
        cellLayout->addWidget(cb);

        connect(cb, qOverload<int>(&QComboBox::currentIndexChanged), this, &QuestionHandlers::answerChanged);

        QWidget *cellWidget = new QWidget(gridContainer);
        cellWidget->setLayout(cellLayout);
        grid->addWidget(cellWidget, i / maxCols, i % maxCols);
    }

    m_multipleCategorizationCombosMap[m_currentQuestionKey] = combos;
    vl->addWidget(gridContainer);
    return parent;
}


// ---------- SEQUENCE AUDIO ----------
QWidget* QuestionHandlers::createSequenceAudio(const QJsonObject &question, QWidget *parent) {
    QVBoxLayout *vl = qobject_cast<QVBoxLayout*>(parent->layout());
    if (!vl) vl = new QVBoxLayout(parent);

    QJsonArray audioOptions = question["audio_options"].toArray();

    m_sequenceSpinBoxes.clear();

    for (int i = 0; i < audioOptions.size(); ++i) {
        QHBoxLayout *hl = new QHBoxLayout;

        QString optionText;
        if (audioOptions[i].isObject()) {
            QJsonObject obj = audioOptions[i].toObject();
            optionText = obj.contains("option") ? obj["option"].toString() : QString("Option %1").arg(i + 1);
        } else {
            optionText = audioOptions[i].toString();
        }

        QPushButton *playBtn = new QPushButton(QString("Play %1").arg(i + 1), parent);
        playBtn->setToolTip(optionText);

        connect(playBtn, &QPushButton::clicked, this, [this, i, audioOptions]() {
            if (m_mediaHandler) {
                QString soundName;
                if (audioOptions[i].isObject()) {
                    QJsonObject obj = audioOptions[i].toObject();
                    soundName = obj["option"].toString();
                } else {
                    soundName = audioOptions[i].toString();
                }
                qDebug() << "Play audio option:" << soundName;
            }
        });

        QSpinBox *order = new QSpinBox(parent);
        order->setRange(1, audioOptions.size());
        order->setToolTip(QString("Set order for %1").arg(optionText));

        m_sequenceSpinBoxes.append(order);

        hl->addWidget(playBtn);
        hl->addWidget(order);

        vl->addLayout(hl);

        connect(order, qOverload<int>(&QSpinBox::valueChanged), this, &QuestionHandlers::answerChanged);
    }

    return parent;
}

// ---------- ORDER PHRASE (FIXED) ----------
QWidget* QuestionHandlers::createOrderPhrase(const QJsonObject &question, QWidget *parent) {
    QVBoxLayout *vl = qobject_cast<QVBoxLayout*>(parent->layout());
    if (!vl) vl = new QVBoxLayout(parent);

    QJsonArray words = question.contains("phrase_shuffled")
        ? question["phrase_shuffled"].toArray()
        : question["words"].toArray();

    m_orderPhraseWords.clear();
    m_orderPhraseLabels.clear();

    for (int i = 0; i < words.size(); ++i) {
        QHBoxLayout *hl = new QHBoxLayout;
        QLabel *lbl = new QLabel(words[i].toString(), parent);
        lbl->setFrameShape(QFrame::Panel);
        lbl->setFrameShadow(QFrame::Raised);
        lbl->setMinimumWidth(300);
        hl->addWidget(lbl);
        m_orderPhraseLabels.append(lbl);

        if (i > 0) {
            QPushButton *upBtn = new QPushButton("↑", parent);
            connect(upBtn, &QPushButton::clicked, this, [this, i]() { moveOrderPhraseWord(i, -1); });
            hl->addWidget(upBtn);
        } else {
            hl->addSpacing(30);
        }
        if (i < words.size() - 1) {
            QPushButton *downBtn = new QPushButton("↓", parent);
            connect(downBtn, &QPushButton::clicked, this, [this, i]() { moveOrderPhraseWord(i, 1); });
            hl->addWidget(downBtn);
        } else {
            hl->addSpacing(30);
        }

        vl->addLayout(hl);
    }
    return parent;
}

void QuestionHandlers::moveOrderPhraseWord(int index, int direction) {
    int newIndex = index + direction;
    if (newIndex < 0 || newIndex >= m_orderPhraseLabels.size()) return;
    QString tmp = m_orderPhraseLabels[index]->text();
    m_orderPhraseLabels[index]->setText(m_orderPhraseLabels[newIndex]->text());
    m_orderPhraseLabels[newIndex]->setText(tmp);
}


// ---------- FILL BLANKS DROPDOWN (FIXED) ----------
QWidget* QuestionHandlers::createFillBlanksDropdown(const QJsonObject &question, QWidget *parent) {
    QVBoxLayout *vl = qobject_cast<QVBoxLayout*>(parent->layout());
    if (!vl) vl = new QVBoxLayout(parent);

    m_fillBlanksDropdowns.clear();

    QJsonArray parts = question["sentence_parts"].toArray();
    QJsonArray blanks = question["options_for_blanks"].toArray();
    int nBlanks = blanks.size();

    QHBoxLayout *row = new QHBoxLayout;
    auto newRow = [&]() {
        if (row->count() > 0) vl->addLayout(row);
        row = new QHBoxLayout;
    };

    for (int i = 0; i < nBlanks; ++i) {
        if (i < parts.size()) {
            QStringList lines = parts[i].toString().split('\n');
            for (int li = 0; li < lines.size(); ++li) {
                if (li > 0) newRow();
                if (!lines[li].isEmpty()) {
                    QLabel *lbl = new QLabel(lines[li], parent);
                    lbl->setWordWrap(true);
                    row->addWidget(lbl);
                }
            }
        }

        QComboBox *cb = new QComboBox(parent);
        if (i < blanks.size()) {
            for (const QJsonValue &opt : blanks[i].toArray())
                cb->addItem(opt.toString());
        }
        m_fillBlanksDropdowns.append(cb);
        row->addWidget(cb);
        connect(cb, qOverload<int>(&QComboBox::currentIndexChanged), this, &QuestionHandlers::answerChanged);
    }

    if (!parts.isEmpty() && parts.size() > nBlanks) {
        QStringList lines = parts.last().toString().split('\n');
        for (int li = 0; li < lines.size(); ++li) {
            if (li > 0) newRow();
            if (!lines[li].isEmpty()) {
                QLabel *lbl = new QLabel(lines[li], parent);
                lbl->setWordWrap(true);
                row->addWidget(lbl);
            }
        }
    }

    if (row->count() > 0) vl->addLayout(row);

    return parent;
}


// ---------- MATCH PHRASES ----------
QWidget* QuestionHandlers::createMatchPhrases(const QJsonObject &question, QWidget *parent) {
    QVBoxLayout *vl = qobject_cast<QVBoxLayout*>(parent->layout());
    if (!vl) vl = new QVBoxLayout(parent);

    QJsonArray pairs = question["pairs"].toArray();
    m_matchPhraseCombos.clear();

    for (int i = 0; i < pairs.size(); ++i) {
        QJsonObject pair = pairs[i].toObject();
        QHBoxLayout *hl = new QHBoxLayout;

        QLabel *lbl = new QLabel(pair["source"].toString(), parent);
        hl->addWidget(lbl);

        QComboBox *cb = new QComboBox(parent);
        for (const QJsonValue &t : pair["targets"].toArray())
            cb->addItem(t.toString());
        m_matchPhraseCombos.append(cb);
        hl->addWidget(cb);

        vl->addLayout(hl);
        connect(cb, qOverload<int>(&QComboBox::currentIndexChanged), this, &QuestionHandlers::answerChanged);
    }

    return parent;
}

// ---------- IMAGE TAGGING ----------
QWidget* QuestionHandlers::createImageTagging(const QJsonObject &question, QWidget *parent) {
    QVBoxLayout *vl = qobject_cast<QVBoxLayout*>(parent->layout());
    if (!vl) vl = new QVBoxLayout(parent);

    int altIdx = m_imageTaggingAltIndex;
    QJsonObject altQ = question;
    if (question.contains("alternatives")) {
        QJsonArray alternatives = question["alternatives"].toArray();
        if (altIdx >= 1 && altIdx < alternatives.size()+1) {
            altQ = alternatives[altIdx-1].toObject();
        }
    }
    QString imgPath;
    if (altQ.contains("media") && altQ["media"].toObject().contains("image")) {
        imgPath = resolveImagePath(altQ["media"].toObject()["image"].toString());
    } else if (altQ.contains("image")) {
        imgPath = resolveImagePath(altQ["image"].toString());
    }

    if (m_imageTaggingWidget) {
        m_imageTaggingWidget->deleteLater();
        m_imageTaggingWidget = nullptr;
    }
    m_imageTaggingWidget = new ImageTaggingWidget(parent);
    m_imageTaggingWidget->setBackgroundImage(imgPath);
    vl->addWidget(m_imageTaggingWidget);

    QJsonArray tagsA = altQ.contains("tags") ? altQ["tags"].toArray() : question["tags"].toArray();
    for (int i = 0; i < tagsA.size(); ++i) {
        QJsonObject tag = tagsA[i].toObject();
        QString tagId = tag["id"].toString();
        QString label = tag["label"].toString();
        QPoint startPos(10, 10 + i * 40);
        if (m_tagPositions.contains(QString::number(altIdx))) {
            QVariantMap altMap = m_tagPositions[QString::number(altIdx)].toMap();
            if (altMap.contains(tagId))
                startPos = altMap[tagId].toPoint();
        }
        m_imageTaggingWidget->addTag(tagId, label, startPos);

        connect(m_imageTaggingWidget, &ImageTaggingWidget::tagPositionChanged,
                this, [this, altIdx](const QString &tId, const QPoint &pos) {
            QVariantMap altMap = m_tagPositions[QString::number(altIdx)].toMap();
            altMap[tId] = pos;
            m_tagPositions[QString::number(altIdx)] = altMap;
        });
    }

    if (question.contains("alternatives")) {
        m_imageTaggingAlternatives = question["alternatives"].toArray();
    } else {
        m_imageTaggingAlternatives = QJsonArray();
    }

    return parent;
}

int QuestionHandlers::getImageTaggingAlternativeCount() const {
    return m_imageTaggingAlternatives.size() > 0 ? m_imageTaggingAlternatives.size() + 1 : 1;
}

void QuestionHandlers::setImageTaggingAlternative(int altIndex)
{
    m_imageTaggingAltIndex = altIndex;
}

QVariantMap QuestionHandlers::getTagPositions() const {
    return m_tagPositions;
}

void QuestionHandlers::setTagPositions(const QVariantMap &positions) {
    m_tagPositions = positions;
}

QString QuestionHandlers::resolveImagePath(const QString &path) const {
    if (QFileInfo(path).isAbsolute()) return path;
    return QDir(m_mediaDir).absoluteFilePath(path);
}

QuestionResult QuestionHandlers::checkAnswer(const QJsonObject& questionBlock, int blockIndex)
{
    QString type = questionBlock.value("type").toString();
    
    if (type == "multi_questions") {
        QuestionResult finalResult;
        finalResult.isCorrect = true;
        QJsonArray innerQuestions = questionBlock["questions"].toArray();
        for(int i = 0; i < innerQuestions.size(); ++i) {
            QJsonObject q = innerQuestions[i].toObject();
            QString qKey = QString("%1-%2").arg(blockIndex).arg(i);
            
            QuestionResult innerResult = checkAnswerDispatcher(q, qKey);
            if(!innerResult.isCorrect) {
                finalResult.isCorrect = false;
                finalResult.message = innerResult.message;
                break; 
            }
        }
        return finalResult;
    } else {
        QString qKey = QString::number(blockIndex);
        return checkAnswerDispatcher(questionBlock, qKey);
    }
}

QuestionResult QuestionHandlers::checkAnswerDispatcher(const QJsonObject& question, const QString& key)
{
    m_currentQuestion = question;
    m_currentQuestionType = question["type"].toString();
    m_currentQuestionKey = key;
    return checkAnswer(question);
}

QuestionResult QuestionHandlers::checkMcqSingle(const QJsonObject &question) {
    QuestionResult r;
    QButtonGroup* group = m_buttonGroups.value(m_currentQuestionKey, m_mcqButtonGroup);
    if (!group) {
        r.message = "Button group not found.";
        return r;
    }
    if (group->checkedId() < 0) {
        r.message = "Please select an answer.";
        return r;
    }
    QJsonArray correctArr = question["answer"].toArray();
    QSet<int> correct;
    for (auto v : correctArr) correct.insert(v.toInt());
    r.isCorrect = correct.contains(group->checkedId());
    r.userAnswer = group->checkedId();
    if (!r.isCorrect) r.message = "Incorrect.";
    return r;
}

QuestionResult QuestionHandlers::checkMcqMultiple(const QJsonObject &question) {
    QuestionResult r;
    QJsonArray correctAnswers = question["answer"].toArray();
    QSet<int> correctIndices;
    for(const auto& ans : correctAnswers) correctIndices.insert(ans.toInt());
    QSet<int> selectedIndices;
    if (m_buttonGroups.contains(m_currentQuestionKey)) {
        QButtonGroup* group = m_buttonGroups.value(m_currentQuestionKey);
        for(QAbstractButton* btn : group->buttons()) {
            if(btn->isChecked()) {
                selectedIndices.insert(group->id(btn));
            }
        }
    } else {
        for (int i = 0; i < m_mcqCheckBoxes.size(); ++i)
            if (m_mcqCheckBoxes[i]->isChecked()) selectedIndices.insert(i);
    }
    r.isCorrect = (selectedIndices == correctIndices);
    QVariantList sel;
    for (int s : selectedIndices) sel.append(s);
    r.userAnswer = sel;
    if (!r.isCorrect) r.message = "Incorrect selection.";
    return r;
}

QuestionResult QuestionHandlers::checkWordFill(const QJsonObject &question) {
    QuestionResult r;
    bool allCorrect = true;
    QVariantList userAnswers;
    QJsonArray correctAnswers = question["answers"].toArray();
    for (int i = 0; i < m_wordFillEntries.size(); ++i) {
        QString entered = m_wordFillEntries[i]->text().trimmed();
        userAnswers.append(entered);
        if (i < correctAnswers.size()) {
            if (entered.compare(correctAnswers[i].toString().trimmed(), Qt::CaseInsensitive) != 0) {
                allCorrect = false;
            }
        } else {
            allCorrect = false;
        }
    }
    r.userAnswer = userAnswers;
    r.isCorrect = allCorrect;
    if (!allCorrect) r.message = "Some answers are incorrect.";
    return r;
}

QuestionResult QuestionHandlers::checkListPick(const QJsonObject &question) {
    QuestionResult result;
    if (!m_listPickWidget) {
        result.message = "List widget not initialized.";
        return result;
    }
    QList<QListWidgetItem *> selectedItems = m_listPickWidget->selectedItems();
    if (selectedItems.isEmpty()) {
        result.message = "Please select at least one option.";
        return result;
    }
    QSet<int> selectedIndices;
    for (QListWidgetItem *item : selectedItems)
        selectedIndices.insert(m_listPickWidget->row(item));
    QSet<int> correctIndices;
    QJsonArray correctArray = question["answer"].toArray();
    for (const QJsonValue &val : correctArray)
        correctIndices.insert(val.toInt());
    result.isCorrect = (selectedIndices == correctIndices);
    QVariantList userSelection;
    for (int idx : selectedIndices)
        userSelection.append(idx);
    result.userAnswer = userSelection;
    if (!result.isCorrect) result.message = "Incorrect selection.";
    return result;
}

QuestionResult QuestionHandlers::checkMatchSentence(const QJsonObject &question) {
    QuestionResult result;
    bool allCorrect = true;
    QVariantMap userAnswers;
    QJsonObject correctMap = question["answer"].toObject();
    QJsonArray pairs = question["pairs"].toArray();
    for (int i = 0; i < pairs.size(); ++i) {
        QJsonObject pair = pairs[i].toObject();
        QString selected = m_matchComboBoxes[i] ? m_matchComboBoxes[i]->currentText() : "";
        QString key;
        if (pair.contains("image_path")) key = pair["image_path"].toString();
        else if (pair.contains("sentence")) key = pair["sentence"].toString();
        userAnswers[key] = selected;
        if (selected != correctMap.value(key).toString())
            allCorrect = false;
    }
    result.userAnswer = userAnswers;
    result.isCorrect = allCorrect;
    if (!allCorrect) result.message = "Incorrect matching.";
    return result;
}

QuestionResult QuestionHandlers::checkCategorization(const QJsonObject &question) {
    QuestionResult r;
    QString selected = m_categorizationCombo ? m_categorizationCombo->currentText() : "";
    r.userAnswer = selected;
    r.isCorrect = (selected == question["correct"].toString());
    if (!r.isCorrect) r.message = "Incorrect category.";
    return r;
}

QuestionResult QuestionHandlers::checkCategorizationMultiple(const QJsonObject &question) {
    QuestionResult r;
    // ✨ Here's the magic! We get the RIGHT combo boxes using our key! ✨
    if (!m_multipleCategorizationCombosMap.contains(m_currentQuestionKey)) {
        r.message = "Could not find widgets to check answer.";
        return r;
    }
    QList<QComboBox*> combosToCheck = m_multipleCategorizationCombosMap.value(m_currentQuestionKey);
    bool all = true;
    QVariantMap answers;
    QJsonArray items = question["stimuli"].toArray();
    QJsonObject correctMap = question["answer"].toObject();
    for (int i = 0; i < combosToCheck.size(); ++i) {
        QString sel = combosToCheck[i]->currentText();
        QString key;
        QJsonObject stim = items[i].toObject();

        // ✨ Here is our new, genius logic! ✨
        // It will use the text if it exists, otherwise it will use the image filename!
        if (stim.contains("text") && stim["text"].isString() && !stim["text"].toString().isEmpty()) {
            key = stim["text"].toString();
        } else if (stim.contains("image") && stim["image"].isString() && !stim["image"].toString().isEmpty()) {
            key = QFileInfo(stim["image"].toString()).fileName();
        }

        answers[key] = sel;

        if (key.isEmpty() || !correctMap.contains(key) || sel != correctMap.value(key).toString())
            all = false;
    }
    r.userAnswer = answers;
    r.isCorrect = all;
    if (!all) r.message = "One or more incorrect.";
    return r;
}

QuestionResult QuestionHandlers::checkSequenceAudio(const QJsonObject &question) {
    QuestionResult r;
    QJsonArray correct = question["answer"].toArray();
    bool allComplete = true;
    bool allCorrect = true;
    QVariantList ans;
    for (int i = 0; i < m_sequenceSpinBoxes.size(); ++i) {
        int val = m_sequenceSpinBoxes[i]->value();
        if (val == 0) allComplete = false;
        ans.append(val - 1);
        if (i < correct.size() && (val - 1) != correct[i].toInt()) {
            allCorrect = false;
        }
    }
    r.userAnswer = ans;
    if (!allComplete) {
        r.message = "Please complete the sequence.";
        return r;
    }
    r.isCorrect = allCorrect;
    if (!allCorrect) r.message = "Incorrect sequence.";
    return r;
}

QuestionResult QuestionHandlers::checkOrderPhrase(const QJsonObject &question) {
    QuestionResult r;
    QStringList correct, attempt;
    for (auto v: question["answer"].toArray()) correct << v.toString();
    for (auto lbl: m_orderPhraseLabels) attempt << lbl->text();
    r.isCorrect = (attempt == correct);
    r.userAnswer = attempt;
    if (!r.isCorrect) r.message = "Phrase order incorrect.";
    return r;
}

QuestionResult QuestionHandlers::checkFillBlanksDropdown(const QJsonObject &question) {
    QuestionResult r;
    bool allCorrect = true;
    QVariantList userAnswers;
    QJsonArray correctAnswers = question["answers"].toArray();
    for (int i = 0; i < m_fillBlanksDropdowns.size(); ++i) {
        QString sel = m_fillBlanksDropdowns[i]->currentText();
        userAnswers.append(sel);
        if (i < correctAnswers.size() && sel != correctAnswers[i].toString()) {
            allCorrect = false;
        }
    }
    r.userAnswer = userAnswers;
    r.isCorrect = allCorrect;
    if (!allCorrect) r.message = "Some blanks incorrect.";
    return r;
}

QuestionResult QuestionHandlers::checkMatchPhrases(const QJsonObject &question) {
    QuestionResult r;
    bool all = true;
    QVariantMap ans;
    QJsonObject correctMap = question["answer"].toObject();
    QJsonArray pairs = question["pairs"].toArray();
    for (int i = 0; i < pairs.size(); ++i) {
        QString source = pairs[i].toObject()["source"].toString();
        QString sel = m_matchPhraseCombos[i]->currentText();
        ans[source] = sel;
        if (sel != correctMap.value(source).toString())
            all = false;
    }
    r.userAnswer = ans;
    r.isCorrect = all;
    if (!all) r.message = "Incorrect matching.";
    return r;
}

QuestionResult QuestionHandlers::checkImageTagging(const QJsonObject &question)
{
    QuestionResult r;
    bool allCorrect = true;
    QJsonObject altObj = question;
    if (m_imageTaggingAltIndex > 0 && m_imageTaggingAltIndex <= m_imageTaggingAlternatives.size()) {
        altObj = m_imageTaggingAlternatives[m_imageTaggingAltIndex - 1].toObject();
    }
    QJsonArray tags = altObj["tags"].toArray();
    QJsonObject answer = altObj["answer"].toObject();
    for (auto tagVal : tags) {
        QJsonObject tagObj = tagVal.toObject();
        QString tagId = tagObj["id"].toString();

        // User's placed position (image coordinates)
        QPointF pos = m_imageTaggingWidget->tagPositionInImage(tagId);

        // Expected/correct position from answer
        double cx = 0, cy = 0;
        if (answer.contains(tagId) && answer[tagId].isArray()) {
            QJsonArray arr = answer[tagId].toArray();
            if (arr.size() >= 2) {
                cx = arr[0].toDouble();
                cy = arr[1].toDouble();
            }
        }
        QPointF correctPos(cx, cy);

        double dist = std::hypot(pos.x() - cx, pos.y() - cy);

        // ✨ Here is our new, fabulous debug message! ✨
        qDebug() << "[ImageTagging] Tag:" << tagId
                << "User placed at (" << pos.x() << "," << pos.y() << ")"
                << "--- Expected at (" << cx << "," << cy << ")"
                << "--- Distance:" << dist;

        // Use a tolerance for placement, e.g. <= 50 pixels
        if (dist > 50)
            allCorrect = false;
    }
    r.isCorrect = allCorrect;
    if (!allCorrect) r.message = "Tags not in correct positions.";
    return r;
}

QuestionResult QuestionHandlers::checkAnswer(const QJsonObject &question) {
    m_currentQuestionType = question["type"].toString();
    if (m_currentQuestionType == "mcq_single") return checkMcqSingle(question);
    if (m_currentQuestionType == "mcq_multiple") return checkMcqMultiple(question);
    if (m_currentQuestionType == "word_fill") return checkWordFill(question);
    if (m_currentQuestionType == "list_pick") return checkListPick(question);
    if (m_currentQuestionType == "match_sentence") return checkMatchSentence(question);
    if (m_currentQuestionType == "categorization") return checkCategorization(question);
    if (m_currentQuestionType == "categorization_multiple") return checkCategorizationMultiple(question);
    if (m_currentQuestionType == "sequence_audio") return checkSequenceAudio(question);
    if (m_currentQuestionType == "order_phrase") return checkOrderPhrase(question);
    if (m_currentQuestionType == "fill_blanks_dropdown") return checkFillBlanksDropdown(question);
    if (m_currentQuestionType == "match_phrases") return checkMatchPhrases(question);
    if (m_currentQuestionType == "image_tagging") return checkImageTagging(question);
    QuestionResult r;
    r.isCorrect = false;
    r.message = "Unknown type.";
    return r;
}