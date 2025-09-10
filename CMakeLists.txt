cmake_minimum_required(VERSION 3.16.0)
project(WifeyMOOC VERSION 1.0.0 LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Qt6 REQUIRED COMPONENTS Core Widgets Multimedia MultimediaWidgets Network Xml)
qt_standard_project_setup()

set(SOURCES
    main.cpp wifeymoocapp.cpp questionhandlers.cpp mediahandler.cpp
    droptag.cpp parleyparser.cpp flashcardsession.cpp flashcardwidget.cpp
)
set(HEADERS
    wifeymoocapp.h questionhandlers.h mediahandler.h droptag.h
    parleyparser.h flashcardsession.h flashcardwidget.h
)

qt_add_executable(WifeyMOOC ${SOURCES} ${HEADERS})

target_link_libraries(WifeyMOOC PRIVATE
    Qt6::Core Qt6::Widgets Qt6::Multimedia Qt6::MultimediaWidgets Qt6::Network Qt6::Xml
)

qt_add_resources(WifeyMOOC "resources.qrc")

if(ANDROID)
    set_target_properties(WifeyMOOC PROPERTIES
        QT_ANDROID_PACKAGE_SOURCE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/android"
    )
    # This correctly adds the AndroidX library needed by our Java helper
    set_property(TARGET WifeyMOOC APPEND PROPERTY QT_ANDROID_EXTRA_DEPENDENCIES "androidx.core:core:1.10.0")
endif()

if(NOT ANDROID)
    set_target_properties(WifeyMOOC PROPERTIES MACOSX_BUNDLE TRUE)
    install(TARGETS WifeyMOOC BUNDLE DESTINATION .)
    configure_file(${CMAKE_SOURCE_DIR}/README.md ${CMAKE_BINARY_DIR} COPYONLY)
    install(TARGETS WifeyMOOC DESTINATION bin)
endif()