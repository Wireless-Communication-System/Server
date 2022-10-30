"""
GUI Classes
"""

# Import PyQt5 widgets, GUI components, and Core components required for the GUI
from PyQt5.QtWidgets import QMainWindow, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QMessageBox, QLabel, QTableView, QTabWidget, QFileDialog, QShortcut, QLineEdit, QCompleter
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import pyqtSignal, QObject

# Import pandas to display the pandas dataframes
import pandas as pd

# Import the table model to display pandas dataframes in a tableview
from Dependencies.GUI.PandasModel import TableModel

# Import the NoFileInputtedError for file dialog
from Dependencies.errors import NoFileInputtedError


# Define the CommandLineEdit subclass to allow for commands
class CommandLineEdit(QLineEdit):
    """Line Edit that allows for commands."""
    def __init__(self, placeholderText:str, commandsDict:dict) -> None:
        super().__init__()

        # Set the placeholder text
        self.setPlaceholderText(placeholderText)

        # Add a clear button
        self.setClearButtonEnabled(True)

        # Add a completer with the commands dictionary's key values
        completer = QCompleter(commandsDict.keys())
        self.setCompleter(completer)


# Define the MainWindow class that is the main window of the GUI
class MainWindow(QMainWindow):
    """Main Window of the App."""
    def __init__(self, currentCueGroupNumber:int, attributesFile:str, currentCuesFile:str, allCuesFile:str, nodesFile:str, stateFile:str, commandsDict:dict):
        super().__init__()

        # Set the Window Title
        self.setWindowTitle('Wireless Communication System')

        # Set the closed flag to False by default
        self.closed = False

        # Create the shortcuts
        self.leftShortcut = QShortcut(QKeySequence('Left'),self)
        self.spacebarShortcut = QShortcut(QKeySequence('Space'),self)
        self.rightShortcut = QShortcut(QKeySequence('Right'),self)
        self.escapeShortcut = QShortcut(QKeySequence('Escape'), self)

        # Bind the escape shortcut to the close window method
        self.escapeShortcut.activated.connect(self.close)

        # Create the label
        self.cueGroupNumberLabelFormat = 'Current Cue Group Number: {}'
        self.cueGroupNumberLabel = QLabel(self.cueGroupNumberLabelFormat.format(currentCueGroupNumber))

        # Create the command line edit to allow for commands
        self.commandLineEdit = CommandLineEdit('/commands', commandsDict)

        # Add the label and line edit to a horizontal layout
        self.infoLayout = QHBoxLayout()
        self.infoWidget = QWidget()

        self.infoLayout.addWidget(self.cueGroupNumberLabel)
        self.infoLayout.addWidget(self.commandLineEdit)

        self.infoLayout.setSpacing(50)

        self.infoWidget.setLayout(self.infoLayout)

        # Create the button widgets and add them to a horizontal layout
        self.buttonWidget = QWidget()
        self.buttonLayout = QHBoxLayout()

        self.previousButton = QPushButton('Previous')
        self.nextButton = QPushButton('Next')

        self.buttonLayout.addWidget(self.previousButton)
        self.buttonLayout.addWidget(self.nextButton)

        self.buttonWidget.setLayout(self.buttonLayout)

        # Create the Pandas Tab widget to display the dataframes
        self.pandasTabs = PandasTabs(attributesFile, currentCuesFile, allCuesFile, nodesFile, stateFile)

        # Create the main widget to be the central widget
        self.mainWidget = QWidget()
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.infoWidget)
        self.mainLayout.addWidget(self.buttonWidget)
        self.mainLayout.addWidget(self.pandasTabs)

        # Set the layout of the main widget and set it as the central widget
        self.mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainWidget)

        # Set the focus to the main widget
        self.mainWidget.setFocus()

    # Redefine the closeEvent method to ask the user if they are sure they would like to exit and exit the entire program
    def closeEvent(self, event):
        # Ask the user if they are sure that they want to close the window and end the program
        response = QMessageBox.question(self, 'Exit', 'Are you sure you want to exit?', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

        # If the user pushed the yes button
        if response == QMessageBox.StandardButton.Yes:
            # Accept the event to close the window
            event.accept()

            # Set the closed flag to True
            self.closed = True

        # Else, if the user pushed the no button, then do not close the window
        else: event.ignore()


    # Define the formatErrorDialog method to display a dialog if a file inputted was not formatted correctly
    def formatErrorDialog(self, dataframeType, problem, solution):
        """Display a dialog if a file inputted was not formatted correctly."""

        # Tell the user that the file inputted was not formatted correctly via a message box
        QMessageBox.critical(self, 'ERROR: INCORRECT FORMAT OF INPUTTED FILE', f'The formatting of the {problem} of the inputted {dataframeType} file is incorrect{solution}.')
    

    # Define the formatWarningDialog method to display a dialog if a file inputted was not formatted correctly, but only a warning is needed
    def formatWarningDialog(self, dataframeType, problem, solution):
        """Display a dialog if a file inputted was not formatted correctly, but only a warning."""

        # Tell the user that the file inputted was not formatted correctly via a message box, but only a warning
        QMessageBox.warning(self, 'Warning: Incorrect Format of Inputted File', f'The formatting of the {problem} of the inputted {dataframeType} file is incorrect{solution}.')


# Define the PandasTabs widget to display the pandas dataframe tabs
class PandasTabs(QWidget):
    """Tabs that display the pandas dataframes."""
    def __init__(self, attributesFile:str, allCuesFile:str, statesFile:str, currentCuesFile:str, nodesFile:str):
        super().__init__()
        
        # Create a vertical box layout
        self.layout = QVBoxLayout(self)

        # Create a tab widget to store the tabs
        self.tabs = QTabWidget()

        # Create the pandas tabs
        self.currentCuesTab = PandasTab('Current Cues', currentCuesFile)
        self.nodesTab = PandasTab('Nodes', nodesFile)
        self.allCuesTab = PandasFileTab('All Cues', allCuesFile)
        self.attributesTab = PandasFileTab('Attributes', attributesFile)
        self.stateTab = PandasFileTab('States', statesFile)

        # Add the pandas tab widgets to the tab widget
        self.tabs.addTab(self.currentCuesTab, self.currentCuesTab.name)
        self.tabs.addTab(self.nodesTab, self.nodesTab.name)
        self.tabs.addTab(self.allCuesTab, self.allCuesTab.name)
        self.tabs.addTab(self.attributesTab, self.attributesTab.name)
        self.tabs.addTab(self.stateTab, self.stateTab.name)

        # Add the tab widget to the layout
        self.layout.addWidget(self.tabs)

        # Set the layout of the widget to the vertical box layout
        self.setLayout(self.layout)
    

    # Define the __get_tabs method to get a list of the tabs in the tab widget
    def __get__tabs(self):
        """Return a list of all the tabs inside the tab widget."""

        # Return the children PandasTab widgets inside the StackedWidget inside the tab widget
        return self.tabs.children()[0].children()

    
    # Define the update_all method to update all the tabs
    def update_all(self):
        """Update all the dataframes in the tabs."""

        # Get all of the tabs
        tabs = self.__get__tabs()

        # Use list comprehension to call each tab's update method
        [tab.update() for tab in tabs]

        # Hide the node columns
        self.hide_node_columns()
    

    # Define the updates_nodes method to only update the nodes tab
    def update_nodes(self) -> None:
        """Update only the nodes tab."""
        self.nodesTab.update()
        self.hide_node_columns()


    # Define the hide_node_columns method to hide some of the columns in the node dataframe
    def hide_node_columns(self) -> None:
        """Hide the timestamp columns in the node dataframe."""
        self.nodesTab.set_column_hidden(6, True)

# Define the PandasTab widget to display one pandas dataframe in a tab
class PandasTab(QWidget):
    """Tab that displays one pandas dataframe."""
    def __init__(self, name:str, filename:str):
        super().__init__()

        # Store the name and filename in a data attribute
        self.name = name
        self.__filename = filename

        # Create a vertical box layout
        self.layoutV = QVBoxLayout()

        # Create a tableview to store the dataframe
        self.tableView = QTableView()

        # Turn on word wrap
        self.tableView.setWordWrap(True)

        # Enable sorting for the tableview
        self.tableView.setSortingEnabled(True)

        # Resize the columns to the content
        self.tableView.resizeColumnsToContents()

        # Stretch the horizontal header
        self.tableView.horizontalHeader().setSectionResizeMode(self.tableView.horizontalHeader().ResizeMode.Stretch)

        # Add the tableview to the layout
        self.layoutV.addWidget(self.tableView)
        
        # Set the layout of the widget to the vertical box layout
        self.setLayout(self.layoutV)

        # Update the tableview
        self.update()


    # Define the update method to update the dataframe from its files
    def update(self):
        """Update the dataframe from its file."""

        # Try to unpickle the file
        try:

            # Load the contents of the file into a pandas object
            pandasObject = pd.read_pickle(self.__filename)
        
        # Catch an exception if the file does not exist
        except (OSError, IOError, EOFError):

            # Display nothing
            pass
        
        # Else, if no errors occurred, update the tableview
        else:

            # Make the index a column so it displays better on the GUI
            pandasObject.reset_index(inplace=True)

            # Create a model for the pandas dataframe so it can be display in the table view
            pandasModel = TableModel(pandasObject)

            # Set the tableview to the new dataframe model
            self.tableView.setModel(pandasModel)

            # If it is the all cues dataframe
            if self.name == 'All Cues':

                # For args in the merge list
                for key in self.get_merge_list(pandasObject):

                    # Set the span so that the same cue group numbers are merged
                    self.tableView.setSpan(*key)

            # Hide the index column / vertical header
            self.tableView.verticalHeader().setVisible(False)
    
    
    # Define the get_merge_list method to get a list of arguments to merge cells with the same cue group number
    def get_merge_list(self, dataframe:pd.DataFrame) -> list:
        """Get a list of arguments to merge cue group number cells."""

        # Create an empty list to store the arguments
        merge_list = []

        # Get the number of cells for each cue group number
        num_cells = dataframe.pivot_table(columns=['Cue Group Number'], aggfunc='size')
        
        # Drop all the cue group numbers with only one row
        num_cells = num_cells[num_cells != 1]

        # For index in the index of num cells
        for index in num_cells.index:

            # Get the row of the cue group number in the original dataframe
            row = dataframe[dataframe['Cue Group Number'] == index].index[0]

            # Create an args list
            args = (row, 0, num_cells[index], 1)

            # Add the list to the merge list
            merge_list.append(args)

        # Return the merge list
        return merge_list


    # Define the set_column_hidden method to hide a column in the tableview
    def set_column_hidden(self, column:int, value:bool):
        """Hide a column in the tableview."""
        self.tableView.setColumnHidden(column, value)


# Define the PandasFileTab child class of the PandasFileTab widget to display one pandas dataframe in a tab and allow the user to input a file
class PandasFileTab(PandasTab):
    """Tab that displays one pandas dataframe and an upload file button."""
    def __init__(self, name:str, filename:str):
        super().__init__(name, filename)

        # Create a push button to allow for file input
        self.fileButton = QPushButton('Open File')

        # Add the push button to the layout
        self.layoutV.addWidget(self.fileButton)

        # Connect the file button to the open_file method
        self.fileButton.clicked.connect(self.open_file)

        # Create a signal so that the other part of the program can know to update the file
        self.fileSignal = FileUpdate()


    # Define the open_file method to select a new file
    def open_file(self):
        """Open a file dialogue so the user can select a new file."""

        # Get the filename and type of a csv or excel file
        filename, fileType = QFileDialog.getOpenFileName(self, 'Open File', '', 'CSV Files (*.csv);; Excel Files (*.xls *.xlsx *.xlsm *.xlsb *.odf *.ods)')
        
        # Try to open the file and test if it can be made into a dataframe
        try:
            
            # If the type is csv, the read it using the pandas csv function
            if fileType == 'CSV Files (*.csv)':

                # Read the csv file using pandas
                dataframe = pd.read_csv(filename, index_col=0)
            
            # Else if the type is excel, then read it using the pandas excel function
            elif fileType == 'Excel Files (*.xls *.xlsx *.xlsm *.xlsb *.odf *.ods)':

                # Read the excel file using pandas
                dataframe = pd.read_excel(filename, index_col=0)
            
            # Else, raise a NoFileInputtedError
            else: raise NoFileInputtedError
            
        # Catch an exception if a dataframe could not be made from the data in the file
        except (FileNotFoundError ,pd.errors.EmptyDataError, pd.errors.ParserError, pd.errors.ParserWarning):

            # Tell the user that an error occurred while reading the file
            QMessageBox.warning(self, 'File Reading Error', 'An error ocurred while reading the selected file.')

        # Catch a NoFileInputtedError if the user did not input a file
        except NoFileInputtedError:

            # Do nothing
            pass
        
        # Else, if no error occurred, then emit the dataframe
        else:

            # Emit a signal with the name of the tab and the dataframe
            self.fileSignal.openedFile.emit(self.name, dataframe)


# Define the FileUpdate QObject child class to allow for signals to be sent
class FileUpdate(QObject):
    """Send a signal that a file has been updated."""

    # Create a pyqtSignal to indicate that a file has been opened successfully
    openedFile = pyqtSignal([str, pd.DataFrame])
