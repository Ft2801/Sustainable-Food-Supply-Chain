# pylint: disable= no-name-in-module,
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
from PyQt5.QtWidgets import (
     QMainWindow, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QWidget, QLineEdit, QLabel, QListWidget, QListWidgetItem, QSplitter
)
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtCore import Qt
from model.certification_model import CertificationModel
from persistence.repository_impl.product_repository_impl import ProductRepositoryImpl
from presentation.controller.guest_controller import ControllerGuest


class LottoTreeView(QMainWindow):
    def __init__(self, lotto_id):
        super().__init__()
        self.setWindowTitle("Catena di Produzione - Lotto")
        self.setGeometry(100, 100, 1000, 600)

        #TODO CONTROLLLER GUEST
        self.manager = ProductRepositoryImpl()
        self.controller = ControllerGuest()
        self.lotto_id = lotto_id

        # Campo CO₂ unitario
        self.co2_unit_field = QLineEdit()
        self.co2_unit_field.setReadOnly(True)
        self.co2_unit_field.setPlaceholderText("Consumo unitario CO₂ (kg/unità)")

        # Cronologia (albero dei lotti)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["ID Lotto", "Tipo", "Quantità Prodotta", "CO₂ Totale (kg)", "Quantità Usata"])
        self.tree.header().setSectionResizeMode(QHeaderView.ResizeToContents)


        # Lista delle certificazioni
        self.certificazioni_list = QListWidget()
        self.certificazioni_list.setMinimumHeight(120)
        self.certificazioni_list.setStyleSheet("background-color: #f9f9f9")

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Consumo unitario CO₂:"))
        layout.addWidget(self.co2_unit_field)

        splitter = QSplitter(Qt.Vertical)
        tree_container = QWidget()
        tree_layout = QVBoxLayout()
        tree_layout.addWidget(QLabel("Catena di produzione:"))
        tree_layout.addWidget(self.tree)
        tree_container.setLayout(tree_layout)

        cert_container = QWidget()
        cert_layout = QVBoxLayout()
        cert_layout.addWidget(QLabel("Certificazioni del lotto:"))
        cert_layout.addWidget(self.certificazioni_list)
        cert_container.setLayout(cert_layout)

        splitter.addWidget(tree_container)
        splitter.addWidget(cert_container)
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.carica_albero_lotti(self.lotto_id, self.tree.invisibleRootItem())
        self.aggiorna_campo_consumo_unitario()
        self.carica_certificazioni_lotto()

    def carica_albero_lotti(self, id_lotto, parent_item, quantita_usata=""):
        lotto = self.manager.carica_lotto_con_composizione(id_lotto)
        if not lotto:
            item = QTreeWidgetItem(["[Lotto non trovato]", "", "", "", ""])
            parent_item.addChild(item)
            return

        # Visualizzazione dettagliata
        item = QTreeWidgetItem([
            str(lotto.id_lotto),
            lotto.tipo or "",
            f"{lotto.quantita:.2f}",
            f"{lotto.cons_co2:.2f}",
            str(quantita_usata) if quantita_usata else ""
        ])
        for i in range(item.columnCount()):
            item.setToolTip(i, item.text(i))  # Tooltip per testi lunghi

        parent_item.addChild(item)

        for comp in lotto.composizione:
            self.carica_albero_lotti(comp.id_lotto_input, item, comp.quantita_utilizzata)

    def aggiorna_campo_consumo_unitario(self):
        lotto = self.manager.carica_lotto_con_composizione(self.lotto_id)
        if lotto:
            try:
                consumo_unitario = lotto.get_costo_totale_lotto_unitario()
                self.co2_unit_field.setText(f"{consumo_unitario:.4f} kg/unità")
            except Exception:
                self.co2_unit_field.setText("Errore nel calcolo")
        else:
            self.co2_unit_field.setText("Lotto non trovato")

    def carica_certificazioni_lotto(self):
        certificati : list[CertificationModel]= self.controller.get_certificazioni_by_lotto(self.lotto_id)
        self.certificazioni_list.clear()

        if not certificati:
            self.certificazioni_list.addItem(QListWidgetItem("Nessuna certificazione trovata per questo lotto."))
            return

        for cert in certificati:
            testo = (
                f"Lotto: {cert.id_lotto}"
                f"📜 {cert.descrizione_certificato} da {cert.nome_azienda} "
                f"(emesso il {cert.data_certificato}, "
                
            )
            item = QListWidgetItem(testo)
            item.setToolTip(testo)
            self.certificazioni_list.addItem(item)
