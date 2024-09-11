import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel,
    QTableWidget, QTableWidgetItem, QFormLayout, QMessageBox, QDialog, QDialogButtonBox)
from PyQt5.QtCore import Qt

def create_database():
    conn = sqlite3.connect('contacts.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            telephone TEXT,
            mail TEXT
        )
    ''')
    conn.commit()
    conn.close()

class EditContactDialog(QDialog):
    def __init__(self, contact_id, current_nom, current_prenom, current_telephone, current_mail):
        super().__init__()
        self.setWindowTitle("Modifier Contact")
        self.contact_id = contact_id
        self.setGeometry(200, 200, 300, 200)
        self.layout = QVBoxLayout(self)

        self.form_layout = QFormLayout()
        self.nom_input = QLineEdit(current_nom)
        self.prenom_input = QLineEdit(current_prenom)
        self.telephone_input = QLineEdit(current_telephone)
        self.mail_input = QLineEdit(current_mail)

        self.form_layout.addRow(QLabel("Nom:"), self.nom_input)
        self.form_layout.addRow(QLabel("Prénom:"), self.prenom_input)
        self.form_layout.addRow(QLabel("Téléphone:"), self.telephone_input)
        self.form_layout.addRow(QLabel("Mail:"), self.mail_input)

        self.layout.addLayout(self.form_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    def get_data(self):
        return {
            'nom': self.nom_input.text(),
            'prenom': self.prenom_input.text(),
            'telephone': self.telephone_input.text(),
            'mail': self.mail_input.text()
        }

class AddressBookApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Carnet d'Adresse")
        self.setGeometry(100, 100, 600, 400)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.init_ui()
        self.load_data()

    def init_ui(self):
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Nom", "Prénom", "Téléphone", "Mail"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.layout.addWidget(self.table)

        self.form_layout = QFormLayout()
        self.nom_input = QLineEdit()
        self.prenom_input = QLineEdit()
        self.telephone_input = QLineEdit()
        self.mail_input = QLineEdit()

        self.form_layout.addRow(QLabel("Nom:"), self.nom_input)
        self.form_layout.addRow(QLabel("Prénom:"), self.prenom_input)
        self.form_layout.addRow(QLabel("Téléphone:"), self.telephone_input)
        self.form_layout.addRow(QLabel("Mail:"), self.mail_input)

        self.layout.addLayout(self.form_layout)

        self.add_button = QPushButton("Ajouter")
        self.add_button.clicked.connect(self.add_contact)
        self.layout.addWidget(self.add_button)

        self.delete_button = QPushButton("Supprimer")
        self.delete_button.clicked.connect(self.delete_contact)
        self.layout.addWidget(self.delete_button)

        self.update_button = QPushButton("Modifier")
        self.update_button.clicked.connect(self.open_edit_dialog)
        self.layout.addWidget(self.update_button)

        self.init_db_button = QPushButton("Initialiser Base de Données")
        self.init_db_button.clicked.connect(self.initialize_database)
        self.layout.addWidget(self.init_db_button)

    def load_data(self):
        self.table.setRowCount(0)
        conn = sqlite3.connect('contacts.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM contacts')
        rows = cursor.fetchall()
        for row in rows:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            for column, data in enumerate(row):
                self.table.setItem(row_position, column, QTableWidgetItem(str(data)))
        conn.close()

    def add_contact(self):
        nom = self.nom_input.text()
        prenom = self.prenom_input.text()
        telephone = self.telephone_input.text()
        mail = self.mail_input.text()
        if not (nom and prenom):
            QMessageBox.warning(self, "Erreur", "Nom et Prénom sont obligatoires")
            return
        conn = sqlite3.connect('contacts.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO contacts (nom, prenom, telephone, mail) VALUES (?, ?, ?, ?)', (nom, prenom, telephone, mail))
        conn.commit()
        conn.close()
        self.load_data()

    def delete_contact(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Erreur", "Sélectionnez une ligne à supprimer")
            return
        contact_id = self.table.item(selected_row, 0).text()  # Récupérer l'ID depuis la première colonne
        conn = sqlite3.connect('contacts.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM contacts WHERE id = ?', (contact_id,))
        conn.commit()
        conn.close()
        self.load_data()

    def open_edit_dialog(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Erreur", "Sélectionnez une ligne à modifier")
            return

        contact_id = self.table.item(selected_row, 0).text()
        current_nom = self.table.item(selected_row, 1).text()
        current_prenom = self.table.item(selected_row, 2).text()
        current_telephone = self.table.item(selected_row, 3).text()
        current_mail = self.table.item(selected_row, 4).text()

        dialog = EditContactDialog(contact_id, current_nom, current_prenom, current_telephone, current_mail)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            self.update_contact(contact_id, data)

    def update_contact(self, contact_id, data):
        conn = sqlite3.connect('contacts.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE contacts SET nom = ?, prenom = ?, telephone = ?, mail = ? WHERE id = ?',
                       (data['nom'], data['prenom'], data['telephone'], data['mail'], contact_id))
        conn.commit()
        conn.close()
        self.load_data()

    def initialize_database(self):
        create_database()
        self.load_data()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AddressBookApp()
    window.show()
    sys.exit(app.exec())
