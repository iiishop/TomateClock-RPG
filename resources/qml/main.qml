import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ApplicationWindow {
    id: root
    visible: true
    width: 460
    height: 760
    minimumWidth: 380
    minimumHeight: 620
    title: "TomateClock RPG"

    color: "#F4E9DF"

    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#F8EDE4" }
            GradientStop { position: 0.45; color: "#F3DECC" }
            GradientStop { position: 1.0; color: "#EACCB4" }
        }
    }

    Rectangle {
        width: Math.min(parent.width - 36, 520)
        height: Math.min(parent.height - 36, 740)
        anchors.centerIn: parent
        radius: 28
        color: "#FFF9F2"
        border.width: 1
        border.color: "#E8C9B0"

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 26
            spacing: 18

            Label {
                text: "TomateClock RPG"
                font.family: "Georgia"
                font.pixelSize: 34
                font.bold: true
                color: "#7D3D28"
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
            }

            Label {
                text: "称号: " + bridge.currentTitle
                font.family: "Microsoft YaHei UI"
                font.pixelSize: 16
                color: "#9B4D33"
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.Wrap
            }

            Item {
                Layout.fillWidth: true
                Layout.preferredHeight: 300

                Canvas {
                    id: ring
                    anchors.centerIn: parent
                    width: Math.min(parent.width - 6, 286)
                    height: width
                    antialiasing: true

                    onPaint: {
                        var ctx = getContext("2d")
                        var cx = width / 2
                        var cy = height / 2
                        var radius = width * 0.41
                        var start = -Math.PI / 2
                        var end = start + (Math.PI * 2 * bridge.progress)

                        ctx.reset()
                        ctx.lineWidth = width * 0.08
                        ctx.strokeStyle = "#E8D1BE"
                        ctx.beginPath()
                        ctx.arc(cx, cy, radius, 0, Math.PI * 2)
                        ctx.stroke()

                        ctx.lineWidth = width * 0.09
                        var gradient = ctx.createLinearGradient(0, 0, width, height)
                        gradient.addColorStop(0.0, "#D4563F")
                        gradient.addColorStop(1.0, "#F19153")
                        ctx.strokeStyle = gradient
                        ctx.lineCap = "round"
                        ctx.beginPath()
                        ctx.arc(cx, cy, radius, start, end, false)
                        ctx.stroke()
                    }
                }

                Rectangle {
                    width: ring.width * 0.68
                    height: width
                    radius: width / 2
                    anchors.centerIn: ring
                    color: "#FFF4EA"
                    border.width: 1
                    border.color: "#E7C7AF"

                    Column {
                        anchors.centerIn: parent
                        spacing: 4

                        Label {
                            id: timeText
                            text: bridge.formattedRemaining
                            font.family: "Consolas"
                            font.bold: true
                            font.pixelSize: 46
                            color: "#8B3D2B"
                            horizontalAlignment: Text.AlignHCenter
                            anchors.horizontalCenter: parent.horizontalCenter
                        }

                        Label {
                            text: bridge.isRunning ? "专注进行中" : "准备开始"
                            font.family: "Microsoft YaHei UI"
                            font.pixelSize: 14
                            color: "#A75C40"
                            horizontalAlignment: Text.AlignHCenter
                            anchors.horizontalCenter: parent.horizontalCenter
                        }
                    }
                }
            }

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 10

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10

                    Repeater {
                        model: bridge.presets

                        delegate: Button {
                            required property int modelData
                            text: modelData + " 分钟"
                            Layout.fillWidth: true
                            enabled: !bridge.isRunning

                            font.family: "Microsoft YaHei UI"
                            font.pixelSize: 14
                            highlighted: bridge.selectedPreset === modelData

                            background: Rectangle {
                                radius: 12
                                color: bridge.selectedPreset === modelData ? "#D56E4A" : "#F6E3D3"
                                border.width: 1
                                border.color: bridge.selectedPreset === modelData ? "#D56E4A" : "#DAB89D"
                            }

                            contentItem: Label {
                                text: parent.text
                                color: bridge.selectedPreset === modelData ? "#FFF8EF" : "#8A4C35"
                                font: parent.font
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                            }

                            onClicked: bridge.choosePreset(modelData)
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    radius: 14
                    color: "#F7E8DB"
                    border.width: 1
                    border.color: "#DDB99E"
                    implicitHeight: customLayout.implicitHeight + 18

                    function applyCustomTime() {
                        bridge.setCustomTime(hourBox.value, minuteBox.value, secondBox.value)
                    }

                    ColumnLayout {
                        id: customLayout
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 8

                        Label {
                            text: "手动时间"
                            font.family: "Microsoft YaHei UI"
                            font.pixelSize: 14
                            font.bold: true
                            color: "#884631"
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            SpinBox {
                                id: hourBox
                                from: 0
                                to: 99
                                value: bridge.manualHours
                                editable: true
                                enabled: !bridge.isRunning
                                Layout.fillWidth: true
                                onValueModified: parent.parent.parent.applyCustomTime()
                            }

                            Label {
                                text: "时"
                                font.family: "Microsoft YaHei UI"
                                font.pixelSize: 14
                                color: "#7B412E"
                            }

                            SpinBox {
                                id: minuteBox
                                from: 0
                                to: 59
                                value: bridge.manualMinutes
                                editable: true
                                enabled: !bridge.isRunning
                                Layout.fillWidth: true
                                onValueModified: parent.parent.parent.applyCustomTime()
                            }

                            Label {
                                text: "分"
                                font.family: "Microsoft YaHei UI"
                                font.pixelSize: 14
                                color: "#7B412E"
                            }

                            SpinBox {
                                id: secondBox
                                from: 0
                                to: 59
                                value: bridge.manualSeconds
                                editable: true
                                enabled: !bridge.isRunning
                                Layout.fillWidth: true
                                onValueModified: parent.parent.parent.applyCustomTime()
                            }

                            Label {
                                text: "秒"
                                font.family: "Microsoft YaHei UI"
                                font.pixelSize: 14
                                color: "#7B412E"
                            }
                        }
                    }

                    Connections {
                        target: bridge

                        function onTotalSecondsChanged() {
                            hourBox.value = bridge.manualHours
                            minuteBox.value = bridge.manualMinutes
                            secondBox.value = bridge.manualSeconds
                        }
                    }
                }
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 12

                Button {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 50
                    text: bridge.isRunning ? "暂停" : "开始专注"
                    font.family: "Microsoft YaHei UI"
                    font.pixelSize: 16
                    font.bold: true

                    background: Rectangle {
                        radius: 14
                        color: bridge.isRunning ? "#BA4D36" : "#D95F3C"
                    }

                    contentItem: Label {
                        text: parent.text
                        color: "#FFF8EF"
                        font: parent.font
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }

                    onClicked: bridge.toggleRun()
                }

                Button {
                    Layout.preferredWidth: 110
                    Layout.preferredHeight: 50
                    text: "重置"
                    font.family: "Microsoft YaHei UI"
                    font.pixelSize: 15

                    background: Rectangle {
                        radius: 14
                        color: "#F0D9C8"
                        border.width: 1
                        border.color: "#D8AF91"
                    }

                    contentItem: Label {
                        text: parent.text
                        color: "#7E402D"
                        font: parent.font
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }

                    onClicked: bridge.resetSession()
                }
            }

            Rectangle {
                Layout.fillWidth: true
                radius: 16
                color: "#F4E4D6"
                border.width: 1
                border.color: "#DFC0A9"
                implicitHeight: infoLayout.implicitHeight + 20

                ColumnLayout {
                    id: infoLayout
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 8

                    Label {
                        text: "累计专注: " + bridge.totalFocusText
                        font.family: "Microsoft YaHei UI"
                        font.pixelSize: 15
                        color: "#7A412F"
                        wrapMode: Text.Wrap
                        Layout.fillWidth: true
                    }

                    Label {
                        text: bridge.nextMilestoneText
                        font.family: "Microsoft YaHei UI"
                        font.pixelSize: 13
                        color: "#8C5A45"
                        wrapMode: Text.Wrap
                        Layout.fillWidth: true
                    }
                }
            }

            Item { Layout.fillHeight: true }
        }
    }

    Rectangle {
        id: levelBanner
        visible: false
        opacity: 0
        radius: 14
        color: "#A7452F"
        border.width: 1
        border.color: "#E5B49A"
        height: 52
        width: Math.min(parent.width - 40, 420)
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        anchors.topMargin: 18
        z: 10

        property string bannerText: ""

        Label {
            anchors.centerIn: parent
            text: levelBanner.bannerText
            font.family: "Microsoft YaHei UI"
            font.pixelSize: 14
            color: "#FFF7EE"
        }
    }

    Timer {
        id: bannerTimer
        interval: 1700
        onTriggered: {
            levelBanner.opacity = 0
            levelBanner.visible = false
        }
    }

    SequentialAnimation {
        id: tickPulse
        running: false
        NumberAnimation { target: timeText; property: "scale"; from: 1.0; to: 1.08; duration: 140 }
        NumberAnimation { target: timeText; property: "scale"; from: 1.08; to: 1.0; duration: 160 }
    }

    NumberAnimation {
        id: bannerFadeIn
        target: levelBanner
        property: "opacity"
        from: 0
        to: 1
        duration: 150
    }

    Connections {
        target: bridge

        function onRemainingSecondsChanged() {
            tickPulse.restart()
            ring.requestPaint()
        }

        function onProgressChanged() {
            // Repaint is handled in onRemainingSecondsChanged to avoid double repaint per tick.
        }

        function onTitleUpgraded(newTitle) {
            levelBanner.bannerText = "称号升级: " + newTitle
            levelBanner.visible = true
            bannerFadeIn.restart()
            bannerTimer.restart()
        }
    }
}
