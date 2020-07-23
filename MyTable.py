from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem


class MyTable(QTableWidget):
    def __init__(self, r, c):
        super(self.__class__, self).__init__(r, c)
        self.setup_ui()

    def setup_ui(self):
        self.cellChanged.connect(self.current_cell)

    def current_cell(self):
        row = self.currentRow()
        col = self.currentColumn()
        value = self.item(row, col)
        value = value.text()
        if "," in value:
            print("replacing: ", value.replace(",", "."))
            value_new = QTableWidgetItem(value.replace(",", "."))
            self.setCurrentCell(row, col)
            self.setItem(row, col, value_new)
        # print("value: ", value, " in cell: ", row, col)
