/**
 *  Copyright © 2010 Digia Plc
 *  Copyright © 2010 Nokia Corporation
 *
 *  All rights reserved.
 *
 *  Nokia and Nokia Connecting People are registered trademarks of
 *  Nokia Corporation.
 *  Java and all Java-based marks are trademarks or registered
 *  trademarks of
 *  Sun Microsystems, Inc. Other product and company names
 *  mentioned herein may be
 *  trademarks or trade names of their respective owners.
 *
 *
 *  Subject to the conditions below, you may, without charge:
 *
 *  ·  Use, copy, modify and/or merge copies of this software and
 *     associated documentation files (the "Software")
 *
 *  ·  Publish, distribute, sub-licence and/or sell new software
 *     derived from or incorporating the Software.
 *
 *
 *  This file, unmodified, shall be included with all copies or
 *  substantial portions
 *  of the Software that are distributed in source code form.
 *
 *  The Software cannot constitute the primary value of any new
 *  software derived
 *  from or incorporating the Software.
 *
 *  Any person dealing with the Software shall not misrepresent
 *  the source of the Software.
 *
 *  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
 *  KIND, EXPRESS OR IMPLIED,
 *  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 *  MERCHANTABILITY, FITNESS FOR A
 *  PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 *  AUTHORS OR COPYRIGHT
 *  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 *  WHETHER IN AN ACTION
 *  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 *  CONNECTION WITH THE
 *  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */
import QtQuick 1.0

Rectangle {
    id: rectangle

    property CLStyle style: CLStyle {}
    property alias text: text.text
    property color colorWhenDefault: style.colorWhenDefault
    property color colorWhenPressed: style.colorWhenPressed
    property color colorWhenHovered: style.colorWhenHovered
    property color colorWhenSelected: style.colorWhenSelected
    property color textColor: style.textColor
    property real roundness: style.roundness
    property color borderColor: style.borderColor
    property int borderWidth: style.borderWidth
    property real fontSize: style.fontSize
    property string fontFamily: style.fontFamily
    property string fontWeight: style.fontWeight
    property color borderColorWhenHovered: style.borderColorWhenHovered
    property color borderColorWhenPressed: style.borderColorWhenPressed
    property color borderColorWhenSelected: style.borderColorWhenSelected

    /* Properties for background images
     * --------------------------------
     * This solution is temporary. Remember performance.
     */
    //Private properties start
    property Gradient nullGradient: Gradient{}
    //Private properties end

    property bool gradientDefaultOn: style.gradientDefaultOn
    property bool gradientHoveredOn: style.gradientHoveredOn
    property bool gradientPressedOn: style.gradientPressedOn
    property bool gradientSelectedOn: style.gradientSelectedOn

    property bool hoveredStateOn: style.hoveredStateOn
    property bool pressedStateOn: style.pressedStateOn

    property Gradient gradientWhenDefault: style.gradientWhenDefault
    property Gradient gradientWhenHovered: style.gradientWhenHovered
    property Gradient gradientWhenPressed: style.gradientWhenPressed
    property Gradient gradientWhenSelected: style.gradientWhenSelected

    property bool disabled: false
    property bool selected: false

    property string textAlign: "center"
    property real leftMargin: 0
    property real rightMargin: 0

    signal clicked()

    Component.onCompleted: {
        if(!hoveredStateOn) stateHovered.destroy();
        if(!pressedStateOn) statePressed.destroy();
    }

    width: text.width + 15
    height: text.height + 15
    color: colorWhenDefault
    smooth: true
    radius: 0.5
    border.color: borderColor
    border.width: borderWidth
    gradient: (gradientDefaultOn)?gradientWhenDefault:nullGradient

    Text {
        id: text

        text: "CLButton"
        anchors.horizontalCenter: if(textAlign == "center") rectangle.horizontalCenter
        anchors.left: if(textAlign == "left") rectangle.left
        anchors.right: if(textAlign == "right" ) rectangle.right
        anchors.rightMargin: rightMargin
        anchors.leftMargin: leftMargin
        anchors.verticalCenter: rectangle.verticalCenter
        font.family: fontFamily
        font.pointSize: 0.001 + fontSize
        color: textColor
        font.weight: fontWeight
    }

    MouseArea {
        id: mouseArea

        anchors.fill: parent
        onClicked: rectangle.clicked()
        hoverEnabled: true
    }

    state: ""

    states: [
    State {
        id: statePressed
        name: "pressed"; when: mouseArea.pressed && !disabled
        PropertyChanges { target: rectangle; gradient: (gradientPressedOn)?gradientWhenPressed:nullGradient; color: colorWhenPressed; }
        PropertyChanges { target: rectangle; border.color: borderColorWhenPressed }
        PropertyChanges { target: rectangle; color: colorWhenPressed}
    },
    State {
        id: stateSelected
        name: "selected"; when: selected
        PropertyChanges { target: rectangle; gradient: (gradientSelectedOn)?gradientWhenSelected:nullGradient; color: colorWhenSelected; }
        PropertyChanges { target: rectangle; border.color: borderColorWhenSelected }
        PropertyChanges { target: rectangle; color: colorWhenSelected}
    },
    State {
        id: stateHovered
        name: "entered"; when: mouseArea.containsMouse && !disabled
        PropertyChanges { target: rectangle; gradient: (gradientHoveredOn)?gradientWhenHovered:nullGradient; color: colorWhenHovered; }
        PropertyChanges { target: rectangle; border.color: borderColorWhenHovered }
        PropertyChanges { target: rectangle; color: colorWhenHovered}
    },
    State {
        id: stateDisabled
        name: "disabled"; when: disabled
        PropertyChanges {target: rectangle; color: if(gradientDefaultOn) "white"; else colorWhenDefault}
        PropertyChanges {target: rectangle; opacity: 0.6}
        PropertyChanges {target: mouseArea; enabled: false}
    }
    ]
}
