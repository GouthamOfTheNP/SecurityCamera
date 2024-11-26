import sqlite3
import sys
from PyQt6.QtWidgets import (QApplication, QPushButton, QLabel, QLineEdit, QDialog, QVBoxLayout, QComboBox,
                             QMainWindow, QTableWidget, QStatusBar, QTableWidgetItem, QToolBar, QGridLayout,
                             QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from db_functions import create_devices_db

create_devices_db()


def edit():
	edit_dialog = EditDialog()
	edit_dialog.exec()


class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle('Device Management System: Peak State')
		self.setMinimumSize(700, 700)

		file_menu_item = self.menuBar().addMenu('&File')
		help_menu_item = self.menuBar().addMenu('&Help')

		add_device_action = QAction(QIcon("icons/add.png"), 'Add Device', self)
		add_device_action.triggered.connect(self.add_device)
		file_menu_item.addAction(add_device_action)

		refresh_devices_action = QAction(QIcon("icons/refresh-button.png"), 'Refresh Devices', self)
		refresh_devices_action.triggered.connect(self.refresh_devices)
		file_menu_item.addAction(refresh_devices_action)

		about_action = QAction('About', self)
		about_action.triggered.connect(self.about)
		help_menu_item.addAction(about_action)

		support_action = QAction('Support', self)
		support_action.triggered.connect(self.support)
		help_menu_item.addAction(support_action)

		search_action = QAction(QIcon("icons/search.png"), 'Search', self)
		search_action.triggered.connect(self.search)
		file_menu_item.addAction(search_action)

		self.table = QTableWidget()
		self.table.setColumnCount(7)
		self.table.setHorizontalHeaderLabels(['ID', 'Device', 'Stock', 'Price', 'Identification', 'Description', 'Image'])
		self.table.verticalHeader().setVisible(False)
		self.setCentralWidget(self.table)

		toolbar = QToolBar()
		toolbar.setMovable(True)
		toolbar.addAction(add_device_action)
		toolbar.addAction(search_action)
		toolbar.addAction(refresh_devices_action)

		self.addToolBar(toolbar)
		self.status_bar = QStatusBar()
		self.setStatusBar(self.status_bar)
		print(type(self.table.currentRow()))
		self.table.cellClicked.connect(self.cell_clicked)
		self.table.cellChanged.connect(self.cell_clicked)
		self.table.currentCellChanged.connect(self.cell_clicked)

	def cell_clicked(self):
		edit_button = QPushButton('Edit Device')
		edit_button.clicked.connect(edit)

		delete_button = QPushButton('Delete Device')
		delete_button.clicked.connect(self.delete)

		children = self.findChildren(QPushButton)
		if children:
			for child in children:
				self.status_bar.removeWidget(child)
		if self.table.currentRow() != -1:
			self.status_bar.addWidget(edit_button)
			self.status_bar.addWidget(delete_button)

	@staticmethod
	def delete():
		delete_dialog = DeleteDialog()
		delete_dialog.exec()

	def load_data(self):
		connection = sqlite3.connect("devices.db")
		cursor = connection.cursor()
		cursor.execute("SELECT * FROM devices")
		results = cursor.fetchall()
		self.table.setRowCount(0)
		for result_number, result_data in enumerate(results):
			self.table.insertRow(result_number)
			for cell_number, cell_data in enumerate(result_data):
				self.table.setItem(result_number, cell_number, QTableWidgetItem(str(cell_data)))
		connection.close()

	@staticmethod
	def add_device():
		dialog = InsertDialog()
		dialog.exec()

	@staticmethod
	def search():
		search_dialog = SearchDialog()
		search_dialog.exec()

	@staticmethod
	def about():
		about_dialog = AboutDialog()
		about_dialog.exec()

	def refresh_devices(self):
		self.load_data()

	@staticmethod
	def support():
		support_dialog = SupportDialog()
		support_dialog.exec()


class InsertDialog(QDialog):
	def __init__(self):
		super().__init__()
		self.file_path = None
		self.setWindowTitle('Add Student')
		self.setFixedSize(400, 250)

		layout = QVBoxLayout()

		self.device_name = QLineEdit()
		self.device_name.setPlaceholderText("Device Name")
		layout.addWidget(self.device_name)

		self.stock = QLineEdit()
		self.stock.setPlaceholderText("Stock")
		layout.addWidget(self.stock)

		self.price = QLineEdit()
		self.price.setPlaceholderText("Price")
		layout.addWidget(self.price)

		self.identification = QLineEdit()
		self.identification.setPlaceholderText("Identification")
		layout.addWidget(self.identification)

		self.desc = QLineEdit()
		self.desc.setPlaceholderText("Description")
		layout.addWidget(self.desc)

		self.file_button = QPushButton("Select Image")
		self.file_button.clicked.connect(self.open_file_dialog)
		layout.addWidget(self.file_button)

		button = QPushButton('Add Device')
		button.clicked.connect(self.add_device)
		layout.addWidget(button)

		self.setLayout(layout)

	def open_file_dialog(self):
		self.file_path, _ = QFileDialog.getOpenFileName(self, 'Open File', '', '*.png *.jpg *.jpeg *.svg *.webp *.tiff')
		if self.file_path:
			print(f"Selected file: {self.file_path}")

	def add_device(self):
		connection = sqlite3.connect("devices.db")
		cursor = connection.cursor()
		if (self.device_name.text() != "" and self.stock.text() != "" and self.identification.text() != ""
				and self.desc.text() != "" and self.price.text() != "" and self.file_path != ""):
			if "static/product_images/" in self.file_path:
				cursor.execute(
					'INSERT INTO devices (device, stock, price, identifier, description, image) VALUES (?, ?, ?, ?, ?, ?)',
					(self.device_name.text(), self.stock.text(), self.price.text(), self.identification.text(),
					 self.desc.text().replace("\n", "<br>"), str(self.file_path).split('static/product_images/')[-1]))
				connection.commit()
				connection.close()
				self.close()
			else:
				QMessageBox.information(self, "Error", "Please select a valid image file located in the static folder")
		else:
			QMessageBox.information(self, "Error", "Please fill in all required fields.")

		main_window.load_data()


class SearchDialog(QDialog):
	def __init__(self):
		super().__init__()
		self.setWindowTitle('Search Device')
		self.setFixedSize(300, 100)

		layout = QVBoxLayout()

		self.device_name = QLineEdit()
		self.device_name.setPlaceholderText('Device Name or Device Identifier')
		layout.addWidget(self.device_name)

		button = QPushButton('Search Device')
		button.clicked.connect(self.search_device)
		layout.addWidget(button)

		self.setLayout(layout)

	def search_device(self):
		name = self.device_name.text()
		connection = sqlite3.connect("devices.db")
		cursor = connection.cursor()
		cursor.execute(f'SELECT device, identifier FROM devices WHERE device = ? OR identifier = ?', (name, name))
		result = cursor.fetchone()
		try:
			items = main_window.table.findItems(result[1], Qt.MatchFlag.MatchFixedString)
			for item in items:
				main_window.table.selectRow(item.row())
				connection.close()
				self.close()
		except TypeError:
			QMessageBox.information(self, "Search Results", "No device found with that name or identifier.")


class EditDialog(QDialog):
	def __init__(self):
		super().__init__()
		self.file_path = None
		self.setWindowTitle('Edit Device')
		self.setFixedSize(400, 250)

		layout = QVBoxLayout()

		index = main_window.table.currentRow()
		if index == -1:
			QMessageBox.warning(self, "No Selection", "Please select a device to edit.")
			self.close()
			self.close()
			return

		device_name = main_window.table.item(index, 1).text()
		self.device_name = QLineEdit(device_name)
		self.device_name.setPlaceholderText("Device Name")
		layout.addWidget(self.device_name)

		stock = main_window.table.item(index, 2).text()
		self.stock = QLineEdit(stock)
		self.stock.setPlaceholderText("Stock")
		layout.addWidget(self.stock)

		price = main_window.table.item(index, 3).text()
		self.price = QLineEdit(price)
		self.price.setPlaceholderText("Price")
		layout.addWidget(self.price)

		identification = main_window.table.item(index, 4).text()
		self.identification = QLineEdit(identification)
		self.identification.setPlaceholderText("ID")
		layout.addWidget(self.identification)

		desc = main_window.table.item(index, 5).text()
		self.desc = QLineEdit(desc)
		self.desc.setPlaceholderText("Description")
		layout.addWidget(self.desc)

		self.image_path = main_window.table.item(index, 6).text() if not None else "aviciitierlist.png"
		self.file_button = QPushButton("Select Image")
		self.file_button.clicked.connect(self.open_file_dialog)
		layout.addWidget(self.file_button)

		self.s_id = main_window.table.item(index, 0).text()

		button = QPushButton("Edit Device")
		button.clicked.connect(self.edit_device)
		layout.addWidget(button)

		self.setLayout(layout)

	def open_file_dialog(self):
		self.file_path, _ = QFileDialog.getOpenFileName(self, 'Open File', self.image_path,
		                                                '*.png *.jpg *.jpeg *.svg *.webp *.tiff')
		if self.file_path:
			print(f"Selected file: {self.file_path}")
			self.file_path = str(self.file_path).split('/')[-1]

	def edit_device(self):
		connection = sqlite3.connect("devices.db")
		cursor = connection.cursor()
		if (self.device_name.text() != "" and self.stock.text() != "" and self.identification.text() != ""
					and self.desc.text() != "" and self.price.text() != "" and self.file_path != ""):
			if self.image_path is not None and ("/" not in self.image_path or "static/product_images/" in self.file_path):
				cursor.execute(
					"UPDATE devices SET device = ?, stock = ?, price = ?, identifier = ?, description = ?, image = ? WHERE id = ?",
					(self.device_name.text(), self.stock.text(), self.price.text(), self.identification.text(),
					 self.desc.text().replace("\n", "<br>"), self.file_path if self.file_path is not None else self.image_path,
					 self.s_id))
				connection.commit()
				connection.close()
				self.close()
			else:
				QMessageBox.information(self, "Error", "Please select a valid image file located in the static folder")
		else:
			QMessageBox.information(self, "Error", "Please fill in all required fields")
		main_window.load_data()


class DeleteDialog(QDialog):
	def __init__(self):
		super().__init__()
		self.setWindowTitle('Delete Device')
		layout = QGridLayout()

		confirmation_message = QLabel('Are you sure you want to delete this record?')
		layout.addWidget(confirmation_message, 0, 0, 1, 2)

		button = QPushButton('Yes, Delete Record')
		button.clicked.connect(self.delete_device)
		layout.addWidget(button, 1, 0)

		button = QPushButton('No, Cancel')
		button.clicked.connect(self.close)
		layout.addWidget(button, 1, 1)

		self.setLayout(layout)

	def delete_device(self):
		connection = sqlite3.connect("devices.db")
		cursor = connection.cursor()
		index = main_window.table.currentRow()
		s_id = main_window.table.item(index, 0).text()
		cursor.execute('DELETE FROM devices WHERE id = ?', (s_id,))
		connection.commit()
		cursor.close()
		connection.close()
		self.close()
		main_window.load_data()

		confirmation_widget = QMessageBox()
		confirmation_widget.setWindowTitle("Success")
		confirmation_widget.setText('Record Deleted')


class AboutDialog(QMessageBox):
	def __init__(self):
		super().__init__()
		self.setWindowTitle('About')
		content = """
This is a simple application that allows you to add, edit and delete devices from the database. This application was built using PyQt6, the professional Python Desktop GUI development library. This application was developed by Goutham Pedinedi as an open-source project. Feel free to create your own application, and feel free to contribute.

Author: Goutham Pedinedi"""
		self.setText(content)


class SupportDialog(QMessageBox):
	def __init__(self):
		super().__init__()
		self.setWindowTitle('Support')
		content = """
Use the plus button to add a device's name, number of items of that item in availability, its description, and the identification tag for the product type.

Use the magnifying glass button to search for a specific item by its identifier or name.

Use the cycle button to refresh the page.

To edit an item, click on any piece of info on the item and click the edit device button (to edit) or the delete device button (to delete).

Author: Goutham Pedinedi"""
		self.setText(content)


if __name__ == "__main__":
	app = QApplication(sys.argv)
	main_window = MainWindow()
	main_window.load_data()
	main_window.show()
	sys.exit(app.exec())
