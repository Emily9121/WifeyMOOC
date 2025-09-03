// parleyparser.h
// This is our magical translator for reading the .kvtml files!
#ifndef PARLEYPARSER_H
#define PARLEYPARSER_H

#include <QString>
#include <QList>
#include <QXmlStreamReader>
#include <QFile>

// A cute little struct to hold our flashcard data
struct Flashcard {
    QString id;
    QString front;
    QString frontExample; // We need this little field to store the example!
    QString back;
    QString backExample; // And this one for the back example!
};

class ParleyParser {
public:
    ParleyParser();
    bool loadFile(const QString& filePath);
    const QList<Flashcard>& getCards() const;
    QString getTitle() const;

private:
    QList<Flashcard> cards;
    QString title;
};

#endif // PARLEYPARSER_H
