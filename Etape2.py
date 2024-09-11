import sys
import sqlite3
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit, QPushButton, QListWidget, QMessageBox
class NoteApp(QWidget):
   def __init__(self):
       super().__init__()
       self.setWindowTitle("Prise de Notes - Méthode Outline")
       # Connexion à la base de données SQLite
       self.conn = sqlite3.connect('notes.db')
       self.cursor = self.conn.cursor()
       self.create_table()
       # Interface utilisateur
       self.layout = QVBoxLayout()
       # Champ de titre
       self.title_input = QLineEdit(self)
       self.title_input.setPlaceholderText("Titre de la note")
       self.layout.addWidget(self.title_input)
       # Champ de contenu
       self.content_input = QTextEdit(self)
       self.content_input.setPlaceholderText("Contenu de la note")
       self.layout.addWidget(self.content_input)
       # Boutons d'ajout et de mise à jour
       button_layout = QHBoxLayout()
       self.add_button = QPushButton("Ajouter")
       self.add_button.clicked.connect(self.add_note)
       button_layout.addWidget(self.add_button)
       self.update_button = QPushButton("Mettre à jour")
       self.update_button.clicked.connect(self.update_note)
       button_layout.addWidget(self.update_button)
       self.layout.addLayout(button_layout)
       # Liste des notes
       self.note_list = QListWidget(self)
       self.note_list.itemClicked.connect(self.load_note)
       self.layout.addWidget(self.note_list)
       # Bouton de suppression
       self.delete_button = QPushButton("Supprimer")
       self.delete_button.clicked.connect(self.delete_note)
       self.layout.addWidget(self.delete_button)
       self.setLayout(self.layout)
       self.load_notes()
   def create_table(self):
       # Création de la table SQLite pour stocker les notes
       self.cursor.execute('''CREATE TABLE IF NOT EXISTS notes
                           (id INTEGER PRIMARY KEY AUTOINCREMENT, titre TEXT NOT NULL, contenu TEXT)''')
       self.conn.commit()
   def load_notes(self):
       # Chargement de toutes les notes dans la liste
       self.note_list.clear()
       self.cursor.execute("SELECT * FROM notes")
       notes = self.cursor.fetchall()
       for note in notes:
           self.note_list.addItem(f"{note[0]} - {note[1]}")
   def add_note(self):
       # Ajout d'une nouvelle note
       titre = self.title_input.text()
       contenu = self.content_input.toPlainText()
       if titre:
           self.cursor.execute("INSERT INTO notes (titre, contenu) VALUES (?, ?)", (titre, contenu))
           self.conn.commit()
           self.load_notes()
           self.title_input.clear()
           self.content_input.clear()
       else:
           QMessageBox.warning(self, "Erreur", "Le titre est obligatoire")
   def load_note(self, item):
       # Chargement de la note sélectionnée dans les champs de saisie
       note_id = item.text().split(" - ")[0]
       self.cursor.execute("SELECT * FROM notes WHERE id=?", (note_id,))
       note = self.cursor.fetchone()
       if note:
           self.title_input.setText(note[1])
           self.content_input.setPlainText(note[2])
   def update_note(self):
       # Mise à jour de la note sélectionnée
       try:
           note_id = self.note_list.currentItem().text().split(" - ")[0]
           titre = self.title_input.text()
           contenu = self.content_input.toPlainText()
           if titre:
               self.cursor.execute("UPDATE notes SET titre=?, contenu=? WHERE id=?", (titre, contenu, note_id))
               self.conn.commit()
               self.load_notes()
           else:
               QMessageBox.warning(self, "Erreur", "Le titre est obligatoire")
       except AttributeError:
           QMessageBox.warning(self, "Erreur", "Veuillez sélectionner une note à mettre à jour")
   def delete_note(self):
       # Suppression de la note sélectionnée
       try:
           note_id = self.note_list.currentItem().text().split(" - ")[0]
           self.cursor.execute("DELETE FROM notes WHERE id=?", (note_id,))
           self.conn.commit()
           self.load_notes()
       except AttributeError:
           QMessageBox.warning(self, "Erreur", "Veuillez sélectionner une note à supprimer")
if __name__ == "__main__":
   app = QApplication(sys.argv)
   window = NoteApp()
   window.show()
   sys.exit(app.exec())
