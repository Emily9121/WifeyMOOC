// parleyparser.cpp
// Here's how we open the .kvtml treasure chest! This file is now fixed! ✨
#include "parleyparser.h"
#include <QDebug>

ParleyParser::ParleyParser() {}

bool ParleyParser::loadFile(const QString& filePath) {
    QFile file(filePath);
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text)) {
        qWarning() << "Cannot open Parley file:" << filePath;
        return false;
    }

    cards.clear();
    title.clear();

    QXmlStreamReader xml(&file);

    QString currentFront;
    QString currentBack;
    QString currentId;
    QString currentTranslationId; // Helper to know if we're in translation 0 or 1

    while (!xml.atEnd() && !xml.hasError()) {
        QXmlStreamReader::TokenType token = xml.readNext();

        if (token == QXmlStreamReader::StartElement) {
            if (xml.name() == QLatin1String("title")) {
                // Using readElementText() here is okay because it's simple
                title = xml.readElementText();
            }
            if (xml.name() == QLatin1String("entry")) {
                currentId = xml.attributes().value("id").toString();
            }
            if (xml.name() == QLatin1String("translation")) {
                // We remember which translation we're inside of
                currentTranslationId = xml.attributes().value("id").toString();
            }
            // --- ✨ Here is the fix! ✨ ---
            // We need to find the <text> tag, and *then* read the characters inside it.
            // readElementText() was skipping ahead too far!
            if (xml.name() == QLatin1String("text")) {
                if (currentTranslationId == "0") {
                    xml.readNext(); // Move to the character data
                    currentFront = xml.text().toString();
                } else if (currentTranslationId == "1") {
                    xml.readNext(); // Move to the character data
                    currentBack = xml.text().toString();
                }
            }
        }

        if (token == QXmlStreamReader::EndElement && xml.name() == QLatin1String("entry")) {
            if (!currentFront.isEmpty() && !currentBack.isEmpty()) {
                cards.append({currentId, currentFront, currentBack});
            }
            // Clear for the next entry
            currentFront.clear();
            currentBack.clear();
            currentId.clear();
            currentTranslationId.clear();
        }
    }

    if (xml.hasError()) {
        qWarning() << "XML error:" << xml.errorString();
        return false;
    }

    return !cards.isEmpty();
}

const QList<Flashcard>& ParleyParser::getCards() const {
    return cards;
}

QString ParleyParser::getTitle() const {
    return title;
}
