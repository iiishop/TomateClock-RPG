import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: root
    width: 460
    height: 700
    visible: true
    title: "TomateClock RPG"
    color: "#fff6eb"

    property color accent: "#e36f47"
    property color accentSoft: "#f8e4d8"
    property color textStrong: "#3a2c28"
    property color textDim: "#6c5651"

    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#fff6eb" }
            GradientStop { position: 1.0; color: "#ffe9dd" }
        }
    }

    Rectangle {
        id: mainCard
        anchors {
            horizontalCenter: parent.horizontalCenter
            verticalCenter: parent.verticalCenter
        }
        width: parent.width - 48
        height: 560
        radius: 28
        color: "#fffdfa"
        border.width: 1
        border.color: "#f2ded3"

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 24
            spacing: 18

            Label {
                text: "TomateClock RPG"
                font.pixelSize: 28
                font.bold: true
                color: root.textStrong
                Layout.alignment: Qt.AlignHCenter
            }

            Label {
                text: "每一次专注都在升级"
                font.pixelSize: 16
                color: root.textDim
                Layout.alignment: Qt.AlignHCenter
            }

            Item { Layout.preferredHeight: 6 }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 170
                radius: 24
                color: root.accentSoft

                Column {
                    anchors.centerIn: parent
                    spacing: 6

                    Text {
                        id: timerText
                        text: timerBridge.remaining_display
                        font.pixelSize: 56
                        font.bold: true
                        color: root.textStrong
                        horizontalAlignment: Text.AlignHCenter
                        anchors.horizontalCenter: parent.horizontalCenter
                        scale: 1.0

                        SequentialAnimation on scale {
                            id: pulseAnim
                            running: false
                            NumberAnimation { to: 1.08; duration: 110; easing.type: Easing.OutQuad }
                            NumberAnimation { to: 1.0; duration: 140; easing.type: Easing.InOutQuad }
                        }
                    }

                    Text {
                        text: timerBridge.is_running ? "专注进行中" : "准备开始"
                        font.pixelSize: 16
                        color: root.textDim
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                }
            }

            Label {
                text: "快速开始"
                font.pixelSize: 15
                font.bold: true
                color: root.textStrong
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 10

                Repeater {
                    model: [10, 15, 25]
                    delegate: Button {
                        required property int modelData
                        text: modelData + " 分钟"
                        Layout.fillWidth: true
                        onClicked: timerBridge.start_preset_minutes(modelData)

                        background: Rectangle {
                            radius: 16
                            color: parent.down ? "#d8613a" : root.accent
                        }
                        contentItem: Text {
                            text: parent.text
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                            color: "#fff9f3"
                            font.pixelSize: 15
                            font.bold: true
                        }
                    }
                }
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 10

                Button {
                    text: "暂停"
                    enabled: timerBridge.is_running
                    Layout.fillWidth: true
                    onClicked: timerBridge.pause()
                }

                Button {
                    text: "继续"
                    enabled: !timerBridge.is_running && timerBridge.remaining_seconds > 0
                    Layout.fillWidth: true
                    onClicked: timerBridge.resume()
                }

                Button {
                    text: "重置"
                    Layout.fillWidth: true
                    onClicked: timerBridge.reset()
                }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 130
                radius: 20
                color: "#fff3e8"
                border.width: 1
                border.color: "#efd9c7"

                Column {
                    anchors.centerIn: parent
                    spacing: 8

                    Text {
                        text: "累计专注: " + timerBridge.total_focus_display
                        color: root.textStrong
                        font.pixelSize: 20
                        font.bold: true
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Text {
                        id: titleLabel
                        text: "当前称号: " + timerBridge.current_title
                        color: root.textDim
                        font.pixelSize: 16
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                }
            }

            Item { Layout.fillHeight: true }
        }
    }

    Popup {
        id: unlockPopup
        modal: false
        focus: false
        x: (root.width - width) / 2
        y: 36
        width: mainCard.width - 40
        height: 64
        closePolicy: Popup.NoAutoClose
        background: Rectangle {
            radius: 14
            color: "#e36f47"
        }

        Label {
            anchors.centerIn: parent
            text: "称号升级: " + titleLabel.text.replace("当前称号: ", "")
            color: "#fff8f4"
            font.pixelSize: 18
            font.bold: true
        }

        enter: Transition {
            NumberAnimation { property: "opacity"; from: 0; to: 1; duration: 140 }
            NumberAnimation { property: "scale"; from: 0.92; to: 1.0; duration: 140 }
        }
        exit: Transition {
            NumberAnimation { property: "opacity"; from: 1; to: 0; duration: 180 }
        }
    }

    Timer {
        id: popupTimer
        interval: 1500
        onTriggered: unlockPopup.close()
    }

    Connections {
        target: timerBridge
        function onRemainingSecondsChanged() {
            pulseAnim.restart()
        }
        function onTitleUnlocked() {
            unlockPopup.open()
            popupTimer.restart()
        }
    }
}
