# pylint: disable= no-name-in-module,
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
# # pylint: disable= invalid-name
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QDesktopWidget, QAction


def is_blank(a):
    for i in a:
        if i == '' or i.isspace():
            return True
    return False


def center(self):
    qr = self.frameGeometry()
    cp = QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    self.move(qr.topLeft())


def add_field_to_form(label, casella, form):
    casella.setStyleSheet(
        "border-radius: 10px; border: 2px solid green; color: black; padding: 5px")
    label.setFont(QFont("Times Roman", 11, QFont.Bold))
    label.setStyleSheet("color: green")
    form.addRow(label, casella)


def insert_button(button, layout):
    button.setFont(QFont("Times Roman", 11, QFont.Bold))
    button.setStyleSheet(
        "background-color: green; border-radius: 15px; color: white; padding: 10px"
    )
    layout.addWidget(button)


def insert_button_in_grid(button, layout, x, y, sviluppatori=False):
    button.setFont(QFont("Times Roman", 11, QFont.Bold))
    button.setStyleSheet(
        "background-color: green; border-radius: 15px; color: white; padding: 10px"
    )
    if sviluppatori:
        button.setStyleSheet(
            "background-color: transparent; border-radius: 55px; border: 2px solid black; padding: 5px"
        )
    layout.addWidget(button, x, y)


def insert_label(label, layout, dim=20, color="color: green"):
    label.setAlignment(Qt.AlignCenter)
    label.setFont(QFont("Times Roman", dim, QFont.Bold))
    label.setStyleSheet(color)
    layout.addWidget(label, alignment=Qt.AlignCenter)


def insert_logo(logo, layout, pixmap):
    logo.setPixmap(pixmap)
    logo.setScaledContents(True)
    logo.setFixedSize(150, 150)
    layout.addWidget(logo, 3, 3)


def insert_list(lista, layout, x=500, y=400):
    lista.setFixedSize(x, y)
    lista.setStyleSheet(stile_liste())
    layout.addWidget(lista, alignment=Qt.AlignCenter)


def stile_checkbox():
    return """
                    QCheckBox {
                        background-color: green;
                        border-radius: 15px;
                        padding: 2px;
                    }
                    QCheckBox::indicator {
                        width: 26px;
                        height: 26px;
                        border-radius: 13px;
                        background-color: white;
                        position: absolute;
                    }
                    QCheckBox::indicator:checked {
                        background-color: white;
                        left: 30px;
                    }
                    QCheckBox::indicator:unchecked {
                        background-color: white;
                        left: 2px;
                    }
                """


def stile_liste():
    return """
                QListView {
                    background-color: white;  /* Colore di sfondo del widget */
                    border: 1px solid green;
                    border-radius: 15px;

                }

                QListView::item {
                    background-color: white;  /* Colore di sfondo degli elementi, simula il padding bianco */
                    border-radius: 10px;  /* Arrotonda gli angoli degli elementi */
                    margin: 10px 10px 0 10px;  /* Spazio tra gli elementi */
                    border: 1px solid green;  /* Bordo degli item */
                    padding: 5px;  /* Spazio tra il contenuto e il bordo */
                }

                QListView::item:selected {
                    background-color: lightgreen;  /* Colore di sfondo dell'elemento selezionato */
                    color: black;  /* Colore del testo dell'elemento selezionato */
                }
                """


def config_widget(main_layout, label, form_layout, form_container, margine, dim=40):
    main_layout.setSpacing(20)
    main_layout.setAlignment(Qt.AlignCenter)

    insert_label(label, main_layout, dim)

    form_layout.setSpacing(10)

    form_container.addLayout(form_layout)
    form_container.setContentsMargins(margine, 0, margine, 0)


def config_menu(menu, items, button):
    for testo, azione in items:
        menu.addAction(testo, azione)
    button.setMenu(menu)


def config_menubar(self, stringa, img, _str2, tasti, menu_bar):
    menu = menu_bar.addMenu(stringa)
    action = QAction(QIcon(img), _str2, self)
    action.setShortcut(tasti)
    menu.addAction(action)
    return action


def timeout():
    """Restituisce il timeout di inattività in millisecondi (30 minuti)"""
    return 30 * 60 * 1000  # 30 minuti in millisecondi
