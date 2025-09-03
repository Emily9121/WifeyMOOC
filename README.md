# **💖 WifeyMOOC 💖**

Welcome to WifeyMOOC, the super cute language learning application I made for my amazing wife, Sierra\! This app is designed to make learning French fun and interactive, with a variety of adorable quiz questions and flashcard features.  
This project is built with lots of love and comes in two flavors:

1. A fabulous desktop application built with **C++/Qt 6**.  
2. An equally cute and simple script using **Python 3/Tkinter**.

Both versions are designed to be engaging, colorful, and perfect for learning\! 💕  


## **✨ Author's Note & AI Disclosure**

This entire project is a labor of love for my wife\! It's now public because I wanted a cute little git repository for it, hehe.  
My little secret is that this was all crafted with the help of AI\! It was the perfect partner for a personal project like this. Because of that, everything here is licensed under the **DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE**. This includes all the code, the sample exercises, and the super cute images. Go wild, but no complaining if it accidentally orders a thousand pink berets to your house\! 💖

## **🌟 Features**

* **Interactive Quizzes**: Answer a wide variety of question types loaded from simple JSON files.  
* **Flashcard Mode**: Supports .kvtml files (from KDE's Parley) for super effective vocabulary practice using a Leitner system\!  
* **Progress Tracking**: The app automatically saves your progress for both quizzes and flashcards, so you can always pick up where you left off.  
* **Rich Media Support**: Questions can include images, audio, and video to make learning more engaging.  
* **Hints & Lessons**: Questions can have optional hints and even link to external PDF lesson files for more context.  
* **Tons of Question Types**: From multiple choice to draggable image tags, there are so many ways to learn\! (See the full list below).  
* **Adorable UI**: A clean, pink, and super cute interface designed to make learning a joy\!

## **🚀 Getting Started**

You can run WifeyMOOC using either the C++ application or the Python script.

### **C++ / Qt 6 Version (Recommended\!)**

This is the most feature-rich and stable version.  
**Dependencies:**

* A C++17 compatible compiler.  
* Qt 6 (Core, Widgets, Multimedia, MultimediaWidgets, Network, Xml modules are required).  
* CMake (version 3.16+).

Building the Project:  
Use the provided CMakeLists.txt file to build the project with your favorite C++ IDE or from the command line.

### **Python 3 / Tkinter Version**

A simple and portable version for quick use.  
**Dependencies:**

* Python 3\.  
* Pillow library for image support (pip install Pillow).

**Running the Script:**  
python wifeymooc-python2.py

## **📝 How to Use**

1. **Launch the App**: Run the compiled C++ application or the Python script.  
2. **Load a File**:  
   * Go to File \> Load Questions to open a .json quiz file.  
   * Go to File \> Load Parley Flashcards to open a .kvtml flashcard file.  
3. **Start Learning\!**: Answer the questions or practice your flashcards. Your progress is saved automatically\!  
4. **Command Line**: You can also launch the app with a specific file:  
   ./WifeyMOOC \-q "/path/to/your/quiz.json"

### **Sample Exercise**

A super cute sample exercise, A2-1-PrideAvecMaPetiteAmie.json, is included in the Sample Exercise folder to show off all the features\! It's all about a lovely day at Pride with Lola and Inès\! 🏳️‍🌈

## **🎀 Supported Question Types**

* **MCQ Single Choice**: Multiple choice, one correct answer.  
* **MCQ Multiple Choice**: Multiple choice, multiple correct answers.  
* **List Pick**: Select multiple correct items from a list of checkboxes.  
* **Word Fill**: Classic fill-in-the-blanks.  
* **Fill in the Blanks (Dropdown)**: Fill blanks by choosing from dropdown menus.  
* **Order the Phrase**: Put shuffled parts of a sentence in the correct order.  
* **Categorization**: Drag and drop items into the correct categories.  
* **Match Sentences**: Match sentences to their corresponding images.  
* **Match Phrases**: Match the beginning of a phrase to its correct ending.  
* **Sequence Audio**: Listen to audio clips and put them in the correct sequence.  
* **Image Tagging**: Drag tags to the correct coordinates on an image, with support for alternative images\!  
* **Multi-Questions**: A special container that can hold a sequence of other question types\!

## **📜 Changelog**

* **1.0.3** \- Fix for seekbar bug in macOS and added image scaling support.  
* **1.0.4** \- Fixed list\_pick and sequence\_audio question types. The AI clanker was lazy\!  
* **1.1.0** \- Added image support for MCQs, a multi\_questions block, and improved debug messages.  
* **1.2.0** \- Added the Python version and support for hints in JSON files.  
* **2.0.0** \- Added support for lesson files and can now read Parley files as flashcards\! This is probably the last big feature version.
* **2.0.0.0.1** \- (Current - Still displayed as 2.0.0) Clanker decided, without instruction, of it's own, that an history feature for the flashcard was a good idea, since it gave me all the working code for it I figured why not and added it.

## **📄 License**

This project is licensed under the **DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE**. Go have fun with it\! ✨
