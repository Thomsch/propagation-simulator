import QtQuick 1.1
import "colibri"

Rectangle {
    id: window

    // Hauteur des composants du haut de l'interface.
    property int headerHeight: 50

    // Largeur des composants sur la gauche de l'interface.
    property int leftWidth: width * 2/3

    // Largeur des composants de droite.
    property int rightWidth: 200

    // Marge des composants par rapport au cadre de la fenêtre.
    property int outerMargin: 30

    // Espacement des composants entre eux.
    property int innerMargin: 10

    width: 600
    height: 400

    Rectangle {
        id: button_bar

        property int buttonWidth: 100
        property int buttonHeight: 30

        height: headerHeight

        anchors.top: parent.top
        anchors.topMargin: outerMargin
        anchors.left: parent.left
        anchors.leftMargin: outerMargin
        anchors.right: context_info.left
        anchors.rightMargin: innerMargin

        visible: true
        border.color: "black"

        Row {
            anchors.leftMargin: 10
            anchors.fill: parent
            spacing: 10

            CLButton {
                id: launch
                width: button_bar.buttonWidth
                height: button_bar.buttonHeight
                text: controller.running?"Pause":"Launch"
                anchors.verticalCenter: parent.verticalCenter
                onClicked: {controller.running?controller.pause_simulation():controller.start_simulation()}
                disabled:controller.stopped
            }

            CLButton {
                id: stop
                width: button_bar.buttonWidth
                height: button_bar.buttonHeight
                text: "Stop"
                anchors.verticalCenter: parent.verticalCenter
                onClicked: {controller.stop_simulation()}
                disabled: !controller.running
            }
        }
    }

    Rectangle {
        id: context_info
        width: rightWidth
        height: headerHeight

        anchors.top: parent.top
        anchors.topMargin: outerMargin
        anchors.rightMargin: outerMargin
        anchors.right: parent.right

        border.color: "#000000"
    }

    Rectangle {
        id: pane_render
        border.color: "black"
        color: "black"

        anchors.top: button_bar.bottom
        anchors.topMargin: innerMargin
        anchors.left: parent.left
        anchors.leftMargin: outerMargin
        anchors.bottom: parent.bottom
        anchors.bottomMargin: outerMargin
        anchors.right: stat_column.left
        anchors.rightMargin: innerMargin

        Image {

            id: render
            objectName: "render"

            property string src: "image://prosim"

            // Calcul des marges pour laisser l'image carré.
            property int horizontalMargin: positive(pane_render.width - pane_render.height) / 2
            property int verticalMargin: positive(pane_render.height - pane_render.width) / 2

            anchors.fill: parent
            anchors.leftMargin: horizontalMargin
            anchors.rightMargin: horizontalMargin
            anchors.bottomMargin: verticalMargin
            anchors.topMargin: verticalMargin

            source: ""
            cache: false

            signal render_updated

            onStatusChanged: if (render.status == Image.Ready) {render.render_updated()}

            // Met à jour le rendu.
            function updateRender() {
                render.source = ""; render.source = render.src;
            }

            // Renvoie val pour autant qu'il soit au dessus de 0. si ce n'est pas le cas,
            // la fonction renvoie 0.
            function positive(val) {
                if(val < 0)
                    return 0
                return val
            }
        }
    }

    Rectangle {
        id: stat_column
        width: rightWidth
        height: leftWidth
        border.color: "#000000"
        anchors.top: context_info.bottom
        anchors.topMargin: innerMargin
        anchors.bottom: parent.bottom
        anchors.bottomMargin: outerMargin
        anchors.right: parent.right
        anchors.rightMargin: outerMargin

        Component {
            id: listDelegate
            Item {
                id: listItem
                anchors.right: parent.right
                anchors.left: parent.left
                height: 25

                Rectangle {
                    id: frame
                    anchors.fill: parent
                    anchors.rightMargin: 5
                    anchors.leftMargin: 5
                    anchors.topMargin: 5
                    anchors.bottomMargin: 5

                    Rectangle {
                        id: itemColor
                        width:model.hasColor?10:0
                        height:model.hasColor?10:0
                        color: model.hasColor?model.color:parent.color
                        anchors.left : parent.left
                        anchors.leftMargin: 5
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    Text {
                        id: itemText
                        text: model.item      // Here we get the value from the model, it's column and it's item
                        anchors.fill: parent
                        anchors.leftMargin: 5 + itemColor.width + (model.hasColor?5:0)
                        verticalAlignment: Text.AlignVCenter
                        horizontalAlignment: Text.AlignLeft
                    }
                }

                Rectangle {
                    id: separator
                    anchors.bottom: parent.bottom
                    anchors.left: parent.left
                    anchors.leftMargin: 5
                    anchors.right: parent.right
                    anchors.rightMargin: 5

                    height: 1
                    color: "gray"
                }
            }
        }

        ListView {
            id: listView
            interactive: false
            anchors.fill: parent
            model: stats // Appel du modèle définit en Python.
            delegate: listDelegate
        }
    }
}
