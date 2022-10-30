"""
Remixed
Credit: Martin Fitzpatrick
https://www.pythonguis.com/tutorials/pyqt6-qtableview-modelviews-numpy-pandas/
"""
from PyQt5.QtCore import Qt, QAbstractTableModel
from PyQt5.QtGui import QFont, QBrush, QColor
from pandas import DataFrame

class TableModel(QAbstractTableModel):

    def __init__(self, data:DataFrame):
        super(TableModel, self).__init__()
        self._data = data

        # Create a merge dictionary to store dictionary to know which cells should be merged
        self.merge_dict = {}


    def data(self, index, role):
        column = index.column()
        row = index.row()

        if role == Qt.ItemDataRole.DisplayRole:
            value = self._data.iloc[row, column]

            # Return the value
            return str(value)
        
        # Else if the role is the BackgroundRole
        elif role == Qt.ItemDataRole.BackgroundRole:
            
            # Get the value at the column and index
            value = str(self._data.iloc[row, column])

            # If the value is related to a go cue, return green
            if value in ('Go', 'Done'):
                color = QColor(0, 255, 0, 100)
                return QBrush(color)
            
            # Else if the value is related to a standby cue, return yellow
            if value in ('Standby', 'Ready'):
                color = QColor(255, 255, 0, 100)
                return QBrush(color)


    def rowCount(self, index):
        return self._data.shape[0]


    def columnCount(self, index):
        return self._data.shape[1]


    def headerData(self, section, orientation, role):
        # section is the index of the column/row.

        # If it is the display role
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Orientation.Vertical:
                return str(self._data.index[section])
        
        # Else if it is the text alignment role
        elif role == Qt.ItemDataRole.TextAlignmentRole:

            # Center align it
            return Qt.AlignCenter
        
        # Else if it is the font role
        elif role == Qt.ItemDataRole.FontRole:
            
            # Create a font that's bold
            font = QFont()
            font.setBold(True)

            # Set the font to bold
            return font         


    def sort(self, column, order):
        """
        Remixed
        Credit: eyllanesc
        https://github.com/eyllanesc/stackoverflow/tree/master/questions/44603119
        """
        colname = self._data.columns.tolist()[column]
        self.layoutAboutToBeChanged.emit()
        self._data.sort_values(colname, ascending= order == Qt.SortOrder.AscendingOrder, inplace=True)
        self.layoutChanged.emit()