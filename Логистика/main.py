import sys
from PyQt5.QtGui import QColor
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QWidget, QPushButton, QLineEdit, QMessageBox
import sqlite3

class OrdersWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Информационная система службы логистики")
        self.setGeometry(100, 100, 1000, 900)

        self.buttonZakaz = QPushButton('Заказы', self)
        self.buttonZakaz.setGeometry(20, 50, 150, 50)
        self.buttonZakaz.clicked.connect(self.openZakaz)

        self.buttonRid = QPushButton('Перевозчики', self)
        self.buttonRid.setGeometry(20, 110, 150, 50)
        self.buttonRid.clicked.connect(self.Riders)

        self.buttonCars = QPushButton('Транспорт', self)
        self.buttonCars.setGeometry(20, 170, 150, 50)
        self.buttonCars.clicked.connect(self.Cars)

        # Create the table widget
        self.table_widget = QTableWidget(self)
        self.table_widget.setGeometry(180, 50, 820, 850)  # Указываем размеры таблицы и ее положение

        self.search_line = QLineEdit(self)
        self.search_line.setGeometry(180, 15, 670, 30)

        self.search_button = QPushButton('Найти', self)
        self.search_button.setGeometry(865, 15, 120, 30)
        self.search_button.clicked.connect(self.searchOrder)

        # Подключаемся к базе данных
        conn = sqlite3.connect('Логистика v5.db')
        cursor = conn.cursor()

        # Получаем данные из таблицы "Заказы2"
        cursor.execute("SELECT * FROM Заказы2")
        data = cursor.fetchall()

        # Устанавливаем количество строк и столбцов в таблице
        self.table_widget.setRowCount(len(data))
        self.table_widget.setColumnCount(len(data[0]))

        # Заполняем таблицу данными
        for row_num, row_data in enumerate(data):
            for col_num, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data))
                self.table_widget.setItem(row_num, col_num, item)

                if col_num == 7:  # Проверяем индекс столбца "Статус"
                    status = str(col_data)
                    if status == "Доставлено":
                        item.setBackground(QColor(0, 255, 0))  # Зеленый цвет
                    elif status == "В пути":
                        item.setBackground(QColor(255, 165, 0))  # Оранжевый цвет
                    elif status == "В обработке":
                        item.setBackground(QColor(255, 0, 0))

            # Устанавливаем заголовки столбцов таблицы
        headers = []
        cursor.execute("PRAGMA table_info(Заказы2)")
        columns = cursor.fetchall()
        for column in columns:
            headers.append(column[1])
        self.table_widget.setHorizontalHeaderLabels(headers)

        # Закрываем соединение с базой данных
        conn.close()

    def openZakaz (self):
        self.zak = OpenZakaz()
        self.zak.show()

    def Riders(self):
        self.rid = OpenRiders()
        self.rid.show()

    def Cars(self):
        self.car = OpenCars()
        self.car.show()

    def searchOrder(self):
        order_number = self.search_line.text()

        # Проверка на ввод чисел
        if not order_number.isdigit():
            QMessageBox.warning(self, 'Ошибка', 'Введите только цифры для поиска номера заказа')
            return

        # Выполним поиск и выделим найденный заказ
        found = False
        status_col_index = 7  # Индекс столбца "Статус"
        for row in range(self.table_widget.rowCount()):
            item = self.table_widget.item(row, 0)  # Номер заказа находится в первом столбце
            if item.text() == order_number:
                for col in range(self.table_widget.columnCount()):
                    if col != status_col_index:  # Пропустим столбец "Статус"
                        item = self.table_widget.item(row, col)
                        item.setBackground(QColor(173, 216, 230))  # Цвет выделения
                found = True
                # Восстановим цвет статуса для найденной строки
                status_item = self.table_widget.item(row, status_col_index)
                status_item.setBackground(self.getStatusColor(status_item.text()))
            else:
                # Сброс цвета для строк, которые не соответствуют запросу, исключая "Статус"
                for col in range(self.table_widget.columnCount()):
                    if col != status_col_index:
                        item = self.table_widget.item(row, col)
                        item.setBackground(QColor(255, 255, 255))  # Белый цвет

        if not found:
            QMessageBox.warning(self, 'Ошибка', 'Заказ с таким номером не найден')

    def getStatusColor(self, status):
        if status == "Доставлено":
            return QColor(0, 255, 0)  # Зеленый цвет
        elif status == "В пути":
            return QColor(255, 165, 0)  # Оранжевый цвет
        elif status == "В обработке":
            return QColor(255, 0, 0)  # Красный цвет
        return QColor(255, 255, 255)  # Белый цвет по умолчанию


class OpenZakaz(QWidget):
    def __init__(self):
        super().__init__()

        self.data_to_save2 = []

        self.setWindowTitle("Заказы")
        self.setGeometry(100, 100, 1000, 900)

        self.history = QPushButton('История заказов', self)
        self.history.setGeometry(10, 10, 150, 30)
        self.history.clicked.connect(self.History)

        self.add_button = QPushButton('Добавить запись', self)
        self.add_button.setGeometry(10, 50, 150, 30)
        self.add_button.clicked.connect(self.add_new_row2)

        self.save_button = QPushButton('Сохранить', self)
        self.save_button.setGeometry(10, 90, 150, 30)
        self.save_button.clicked.connect(self.save_to_database2)

        self.delete_button = QPushButton('Удалить', self)
        self.delete_button.setGeometry(10, 130, 150, 30)
        self.delete_button.clicked.connect(self.delete_row2)

        self.table_widget = QTableWidget(self)
        self.table_widget.setGeometry(170, 10, 820, 800)

        conn = sqlite3.connect('Логистика v5.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Заказы")
        data = cursor.fetchall()

        self.table_widget.setRowCount(len(data))
        self.table_widget.setColumnCount(len(data[0]))

        for row_num, row_data in enumerate(data):
            for col_num, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data))
                self.table_widget.setItem(row_num, col_num, item)

                if col_num == 7:
                    status = str(col_data)
                    if status == "Доставлено":
                        item.setBackground(QColor(0, 255, 0))
                    elif status == "В пути":
                        item.setBackground(QColor(255, 165, 0))
                    elif status == "В обработке":
                        item.setBackground(QColor(255, 0, 0))

        headers = [column[1] for column in cursor.execute("PRAGMA table_info(Заказы)")]
        self.table_widget.setHorizontalHeaderLabels(headers)

        conn.close()

    def add_new_row2(self):
        row_position = self.table_widget.rowCount()
        self.table_widget.insertRow(row_position)

        new_data = ["" for _ in range(self.table_widget.columnCount())]
        self.data_to_save2.append(new_data)

    def delete_row2(self):
        selected_row = self.table_widget.currentRow()

        if selected_row != -1:
            id_to_delete = self.table_widget.item(selected_row, 0).text()
            self.table_widget.removeRow(selected_row)
            if selected_row < len(self.data_to_save2):
                del self.data_to_save2[selected_row]
            else:
                print("Ошибка: Индекс строки для удаления вне диапазона.")

            self.delete_from_database2(id_to_delete)

    def delete_from_database2(self, id_to_delete):
        try:
            conn = sqlite3.connect('Логистика v5.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Заказы WHERE ID_Заказа =?", (id_to_delete,))
            conn.commit()
            conn.close()
            print("Данные успешно удалены из базы данных.")
        except Exception as e:
            print("Ошибка при удалении данных:", e)

    def save_to_database2(self):
        try:
            conn = sqlite3.connect('Логистика v5.db')
            cursor = conn.cursor()
            for row_position, data_row in enumerate(self.data_to_save2):
                id_value = data_row[0] if data_row else ""  # Assuming ID is at position 0
                if id_value:  # If there is an ID, it means it's an existing row
                    cursor.execute(
                        "UPDATE Заказы SET ID_Перевозчика=?, ID_Транспорта=?, ID_Заказчика=?, Маршрут=?, Дата_погрузки=?, Дата_доставки=?, Статус=? WHERE ID_Заказа=?",
                        (data_row[1], data_row[2], data_row[3], data_row[4], data_row[5], data_row[6], data_row[7],
                         id_value))
                else:
                    cursor.execute(
                        "INSERT INTO Заказы (ID_Перевозчика, ID_Транспорта, ID_Заказчика, Маршрут, Дата_погрузки, Дата_доставки, Статус) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (data_row[1], data_row[2], data_row[3], data_row[4], data_row[5], data_row[6], data_row[7]))
                print(cursor.lastrowid)
            conn.commit()
            conn.close()
            print("Данные успешно сохранены в базе данных.")
        except Exception as e:
            print("Ошибка при сохранении данных:", e)

    def History(self):
        self.hz = OpenHistory()
        self.hz.show()


class OpenRiders(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Перевозчики")
        self.setGeometry(100, 100, 1000, 900)

        self.table_widget = QTableWidget(self)
        self.table_widget.setGeometry(170, 10, 820, 800)  # Указываем размеры таблицы и ее положение

        conn = sqlite3.connect('Логистика v5.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Перевозчики")
        data = cursor.fetchall()

        self.table_widget.setRowCount(len(data))
        self.table_widget.setColumnCount(len(data[0]))

        for row_num, row_data in enumerate(data):
            for col_num, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data))
                self.table_widget.setItem(row_num, col_num, item)

                if col_num == 4:  # Проверяем индекс столбца "Статус"
                    status = str(col_data)
                    if status == "Заказан":
                        item.setBackground(QColor(0, 255, 0))
                    elif status == "Свободен":
                        item.setBackground(QColor(255, 0, 0))

        headers = []
        cursor.execute("PRAGMA table_info(Перевозчики)")
        columns = cursor.fetchall()
        for column in columns:
            headers.append(column[1])
        self.table_widget.setHorizontalHeaderLabels(headers)

        conn.close()

        self.add_button = QPushButton('Добавить запись', self)
        self.add_button.setGeometry(10, 10, 150, 30)
        self.add_button.clicked.connect(self.add_new_row1)

        self.save_button = QPushButton('Сохранить', self)
        self.save_button.setGeometry(10, 50, 150, 30)
        self.save_button.clicked.connect(self.save_to_database1)

        self.delete_button = QPushButton('Удалить', self)
        self.delete_button.setGeometry(10, 90, 150, 30)
        self.delete_button.clicked.connect(self.delete_row1)

        self.data_to_save = []  # Список для хранения данных для сохранения

    def add_new_row1(self):
        row_position = self.table_widget.rowCount()
        self.table_widget.insertRow(row_position)

        # Создание пустых ячеек для новой строки
        for col_num in range(self.table_widget.columnCount()):
            new_item = QTableWidgetItem("")
            self.table_widget.setItem(row_position, col_num, new_item)

        # Добавляем пустой список для новой строки данных
        self.data_to_save.append([""] * self.table_widget.columnCount())

    def delete_row1(self):
        selected_row = self.table_widget.currentRow()

        if selected_row != -1:
            id_to_delete = self.table_widget.item(selected_row, 0).text()  # Получаем id строки для удаления
            self.table_widget.removeRow(selected_row)
            if selected_row < len(self.data_to_save):
                del self.data_to_save[selected_row]
            else:
                print("Ошибка: Индекс строки для удаления вне диапазона.")

            self.delete_from_database1(id_to_delete)  # Вызываем метод delete_from_database1 для удаления данных из базы данных

    def delete_from_database1(self, id_to_delete):
        try:
            conn = sqlite3.connect('Логистика v5.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Перевозчики WHERE id=?", (id_to_delete,))
            conn.commit()
            conn.close()
            print("Данные успешно удалены из базы данных.")
        except Exception as e:
            print("Ошибка при удалении данных:", e)

    def save_to_database1(self):
        try:
            conn = sqlite3.connect('Логистика v5.db')
            cursor = conn.cursor()
            for row_position in range(self.table_widget.rowCount()):
                values = [self.table_widget.item(row_position, col).text() for col in
                          range(1, self.table_widget.columnCount())]  # пропускаем values[0], который соответствует id
                cursor.execute("SELECT id FROM Перевозчики WHERE id=?",
                               (self.table_widget.item(row_position, 0).text(),))
                existing_row = cursor.fetchone()
                if existing_row:  # Если запись с таким id уже существует, обновляем данные
                    cursor.execute(
                        "UPDATE Перевозчики SET Тип_транспорта=?, Контактная_информация=?, Контактное_лицо=?, Статус=? WHERE id=?",
                        (values[0], values[1], values[2], values[3], self.table_widget.item(row_position, 0).text()))
                else:  # Если запись с таким id не существует, вставляем новую запись
                    cursor.execute(
                        "INSERT INTO Перевозчики (id, Тип_транспорта, Контактная_информация, Контактное_лицо, Статус) VALUES (?, ?, ?, ?, ?)",
                        (self.table_widget.item(row_position, 0).text(), values[0], values[1], values[2], values[3]))
                print(cursor.lastrowid)  # выводим lastrowid после выполнения вставки или обновления
            conn.commit()
            conn.close()
            print("Данные успешно сохранены в базе данных.")
        except Exception as e:
            print("Ошибка при сохранении данных:", e)


class OpenCars(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Транспорт")
        self.setGeometry(100, 100, 1000, 900)

        self.table_widget = QTableWidget(self)
        self.table_widget.setGeometry(170, 10, 820, 800)

        conn = sqlite3.connect('Логистика v5.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Транспорт")
        data = cursor.fetchall()

        self.table_widget.setRowCount(len(data))
        self.table_widget.setColumnCount(len(data[0]))

        for row_num, row_data in enumerate(data):
            for col_num, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data))
                self.table_widget.setItem(row_num, col_num, item)

                if col_num == 3:
                    status = str(col_data)
                    if status == "Активен":
                        item.setBackground(QColor(0, 255, 0))
                    elif status == "Свободен":
                        item.setBackground(QColor(255, 0, 0))

        headers = []
        cursor.execute("PRAGMA table_info(Транспорт)")
        columns = cursor.fetchall()
        for column in columns:
            headers.append(column[1])
        self.table_widget.setHorizontalHeaderLabels(headers)

        conn.close()

        self.add_button = QPushButton('Добавить запись', self)
        self.add_button.setGeometry(10, 10, 150, 30)
        self.add_button.clicked.connect(self.add_new_row)

        self.delete_button = QPushButton('Удалить запись', self)  # Добавляем кнопку удаления
        self.delete_button.setGeometry(10, 90, 150, 30)
        self.delete_button.clicked.connect(self.delete_row)

        self.save_button = QPushButton('Сохранить', self)
        self.save_button.setGeometry(10, 50, 150, 30)
        self.save_button.clicked.connect(self.save_to_database)


        self.data_to_save = []  # Список для хранения данных для сохранения

    def add_new_row(self):
        row_position = self.table_widget.rowCount()
        self.table_widget.insertRow(row_position)

        # Создание пустых ячеек для новой строки
        for col_num in range(self.table_widget.columnCount()):
            new_item = QTableWidgetItem("")
            self.table_widget.setItem(row_position, col_num, new_item)

        # Добавляем пустой список для новой строки данных
        self.data_to_save.append([])

    def delete_row(self):
        selected_row = self.table_widget.currentRow()

        if selected_row != -1:
            self.table_widget.removeRow(selected_row)
            if selected_row < len(self.data_to_save):
                del self.data_to_save[selected_row]
            else:
                print("Ошибка: Индекс строки для удаления вне диапазона.")

    def save_to_database(self):
        conn = sqlite3.connect('Логистика v5.db')
        cursor = conn.cursor()

        try:
            # Удаляем все данные из базы данных
            cursor.execute("DELETE FROM Транспорт")

            # Вставляем новые данные
            for row_position in range(self.table_widget.rowCount()):
                values = [self.table_widget.item(row_position, col).text() for col in
                          range(self.table_widget.columnCount())]

                cursor.execute(
                    "INSERT INTO Транспорт (id, Тип_транспорта, Номер_транспортного_средства, Статус) VALUES (?, ?, ?, ?)",
                    (values[0], values[1], values[2], values[3]))

            conn.commit()
            conn.close()

            print("Данные успешно сохранены в базе данных.")
        except Exception as e:
            print("Ошибка при сохранении данных:", e)


class OpenHistory(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("История заказов")
        self.setGeometry(100, 100, 1000, 900)

        self.table_widget = QTableWidget(self)
        self.table_widget.setGeometry(100, 10, 820, 800)  # Указываем размеры таблицы и ее положение

        conn = sqlite3.connect('Логистика v5.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM История_заказов")
        data = cursor.fetchall()

        self.table_widget.setRowCount(len(data))
        self.table_widget.setColumnCount(len(data[0]))

        for row_num, row_data in enumerate(data):
            for col_num, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data))
                self.table_widget.setItem(row_num, col_num, item)

                if col_num == 7:  # Проверяем индекс столбца "Статус"
                    status = str(col_data)
                    if status == "Доставлено":
                        item.setBackground(QColor(0, 255, 0))  # Зеленый цвет

        headers = []
        cursor.execute("PRAGMA table_info(История_заказов)")
        columns = cursor.fetchall()
        for column in columns:
            headers.append(column[1])
        self.table_widget.setHorizontalHeaderLabels(headers)

        conn.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = OrdersWindow()
    window.show()
    sys.exit(app.exec_())