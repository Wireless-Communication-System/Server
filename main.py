"""
Wireless Communication System
Server Code
"""

# Import the pandas module for storing information
import pandas as pd

# Import the asyncio module to allow for multiple methods to run at the same time
import asyncio

# Import the required classes for the GUI from PyQt5
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QFile, QTextStream

# Import argv from sys to allow for command line arguments in the GUI
from sys import argv

# Import the ErrorStorage class to log errors and the custom exceptions
from Dependencies.errors import ErrorStorage, FormatError, FormatWarning, InvalidCommandInput, Stop

# Import the Communication class to communicate with the ALFRED server
from Dependencies.Communication import Communication

# Import the ServerDataManagement class to manage the dataframes
from Dependencies.DataManagement.Server import ServerDataManagement

# Import the GUI classes for the GUI
from Dependencies.GUI import MainWindow
import Dependencies.GUI.breeze_resources

class Server(QApplication):
    """Communicates with the nodes on the mesh network through the ALFRED server."""
    def __init__(self, attributesFile:str, allCuesFile:str, statesFile:str, currentCuesFile:str, nodesFile:str, cueNumFile:str, errorStorageFile:str, commandsDict:dict):
        super().__init__(argv)

        # Set the stylesheet to breeze dark
        file = QFile(":/dark/stylesheet.qss")
        file.open(QFile.ReadOnly | QFile.Text)
        stream = QTextStream(file)
        self.setStyleSheet(stream.readAll())

        # Create a dictionary with the datatype numbers for each type of data
        self.__datatype_dict = {
            'Online': 65,
            'Attributes': 68,
            'Cue to Node': 69,
            'Current': 70,
            'Node': 71
        }

        # Create a ServerDataManagement object to manage the dataframes
        self.__data = ServerDataManagement(attributesFile, allCuesFile, statesFile, currentCuesFile, nodesFile, cueNumFile, commandsDict)

        # Create an ErrorStorage object to store errors
        self.__errorStorage = ErrorStorage(errorStorageFile)

        # Create a Communication object to communicate with the ALFRED server
        self.__communication = Communication()


    # Define the run_tasks method to concurrently (at the same time) run each part of the server
    async def run_tasks(self):

        try:

            # Gather and store the setup tasks in a data attribute
            self.__setup_tasks = asyncio.gather(

                # Set up the GUI
                self.__setup_GUI()
            )

            # Schedule each task concurrently
            self.__tasks = asyncio.gather(

                # Try to let the nodes know that the server is up-to-date
                self.__uptodate_update(),

                # Perform the setup tasks before allowing some other tasks to run
                self.__setup_tasks,

                # Send the node attributes to the nodes
                self.__send_attributes(),

                # Send the states to the nodes
                self.__send_states(),

                # Send the current cues to the nodes
                self.__send_current_cues(),

                # Get the node series from the nodes
                self.__get_node_series(),

                # Run the GUI
                self.__run_GUI(),

                # Update the last updated column
                self.__update_node_times()
            )
            
            # Run the tasks
            await self.__tasks

        # Catch a Stop exception
        except Stop:
            # Cancel all the tasks
            await self.__cancel_tasks()

        # Catch all other exceptions and log them
        except Exception:

            # Add the error to storage
            self.__errorStorage.update()

    # Define the __cancel_tasks method to properly cancel the asyncio tasks
    async def __cancel_tasks(self):
        """Cancel all the tasks."""
        [task.cancel() for task in self.__tasks if not(task.done())]


    # Define the __uptodate_update method to try to let the nodes know that the server is up-to-date
    async def __uptodate_update(self):
        # Forever
        while True:

            # Get the current timestamp
            serverTime = pd.Timestamp.now()

            # Send the server's timestamp to the nodes
            self.__communication.send_message(serverTime, self.__datatype_dict['Online'])

            # Sleep for 0.25 seconds to allow other tasks to run
            await asyncio.sleep(0.25)

    # Define the __update_attributes method to update the node attributes according to the user and sending the attributes to the nodes
    async def __send_attributes(self):
        """Update the attributes dataframe based on the user inputted data and send it to the nodes."""

        # Wait for the setup tasks to finish
        await self.__setup_tasks

        # Forever
        while True:

            # Send the attributes to the nodes
            self.__communication.send_message(self.__data.attributes.get_data(), self.__datatype_dict['Attributes'])

            # Wait for 2 seconds
            await asyncio.sleep(2)


    # Define the __send_states method to send the state dataframe to the nodes
    async def __send_states(self):
        """Send the state dataframe to the nodes."""

        # Wait for the setup tasks to finish
        await self.__setup_tasks

        # Forever
        while True:

            # Send the state frame to the nodes
            self.__communication.send_message(self.__data.states.get_data(), self.__datatype_dict['Cue to Node'])

            # Wait for 2.5 seconds
            await asyncio.sleep(2.5)


    # Define the __send_current_cues method to dedicate a task to just sending the current cues to the nodes
    async def __send_current_cues(self):
        # Wait for the setup tasks to finish
        await self.__setup_tasks

        # Forever
        while True:

            # Send the dataframe with all the current cues to the nodes
            self.__communication.send_message(self.__data.currentCues.get_data(), self.__datatype_dict['Current'])

            # Wait for 0.1 seconds to allow other tasks to run
            await asyncio.sleep(0.1)


    # Define the __get_node_series method to receive the node series from the nodes
    async def __get_node_series(self):
        """Get the node series from the nodes and format them into a dataframe."""

        # Wait for the setup tasks to finish
        await self.__setup_tasks

        # Forever
        while True:

            # Receive the node series from the nodes
            node_series_list = self.__communication.receive_data(self.__datatype_dict['Node'])

            # If the list is not None
            if node_series_list != None:

                # Update the node dataframe
                self.__data.format_nodes(node_series_list)

                # Update the nodes tab
                self.__mainWindow.pandasTabs.update_nodes()

            # Sleep for 0.3 seconds to allow other tasks to run
            await asyncio.sleep(0.3)


    # Define the async update_node_times method to update the Last Update column on the nodes dataframe
    async def __update_node_times(self) -> None:
        """Update the Last Update column on the nodes dataframe and update the GUI."""

        # Wait for the setup tasks to finish
        await self.__setup_tasks

        # Forever
        while True:

            # Format the timestamps in the nodes frame into the last updated values
            self.__data.update_last_updated()

            # Update the nodes tab
            self.__mainWindow.pandasTabs.update_nodes()

            # Sleep for 60 seconds to allow other tasks to run
            await asyncio.sleep(60)


    # Define the __setup_GUI method to set up the PyQt6 GUI
    async def __setup_GUI(self):
        """Set up the GUI"""

        # Create the main window
        self.__mainWindow = MainWindow(*self.__data.get_main_window_args())

        # Connect the buttons
        self.__mainWindow.previousButton.clicked.connect(self.__previous_cue)
        self.__mainWindow.nextButton.clicked.connect(self.__next_cue)

        # Connect the shortcuts
        self.__mainWindow.leftShortcut.activated.connect(self.__previous_cue)
        self.__mainWindow.spacebarShortcut.activated.connect(self.__next_cue)
        self.__mainWindow.rightShortcut.activated.connect(self.__next_cue)


        # Connect the file signals
        self.__mainWindow.pandasTabs.allCuesTab.fileSignal.openedFile.connect(self.__update_dataframe)
        self.__mainWindow.pandasTabs.attributesTab.fileSignal.openedFile.connect(self.__update_dataframe)
        self.__mainWindow.pandasTabs.stateTab.fileSignal.openedFile.connect(self.__update_dataframe)

        # Connect the command line edit
        self.__mainWindow.commandLineEdit.returnPressed.connect(self.__command_line_input)

        # Show the main window
        self.__mainWindow.showFullScreen()


    # Define the __update_GUI method to update the current cue group label and dataframe tabs in the GUI
    def __update_GUI(self):
        """Update the current cue group label and dataframe tabs in the GUI."""

        # Update the label with the current cue number
        self.__mainWindow.cueGroupNumberLabel.setText(self.__mainWindow.cueGroupNumberLabelFormat.format(self.__data.cueNum))

        # Update the dataframe tabs
        self.__mainWindow.pandasTabs.update_all()

    # Define the __previous_cue method so that the __update_GUI method can be called
    def __previous_cue(self) -> None:
        """Go to the previous cue."""
        self.__data.previous_cue()
        self.__update_GUI()


    # Define the __next_cue method so that the __update_GUI method can be called
    def __next_cue(self) -> None:
        """Advance to the next cue."""
        self.__data.next_cue()
        self.__update_GUI()


    # Define the __set_command_line_text to set the displayed text of the command line edit
    def __set_command_line_text(self, text:str) -> None:
        """Set the displayed text of the command line"""
        self.__mainWindow.commandLineEdit.setText(text)


    # Define the __command_line_input method to run a command
    def __command_line_input(self) -> None:
        """Run a command from the command line edit."""

        # Get the currently displayed text
        command = self.__mainWindow.commandLineEdit.displayText()

        # Split the command by whitespaces
        split_command = command.split()

        # Try to get the command
        try:

            # If the split command's length is greater that 0 and starts with a /
            if len(split_command) > 0 and split_command[0][0] == '/':

                # If the command is /goto cue
                if split_command[0:2] == ['/goto', 'cue']:

                    # If the last index is an integer
                    if split_command[-1].isdigit():

                        # Get the cue number from the command
                        cueNum = int(split_command[-1])

                        # Try to warp to that cue
                        success = self.__data.warp_cue(cueNum)

                        # If the cue number was invalid, then raise an InvalidCommandInput exception
                        if not success:

                            raise InvalidCommandInput('invalid cue group number')
                
                # Else if the command starts with /save
                elif split_command[0] == '/save':

                    # Get the rest of the command as a string, which should be the show's folder name
                    folderName = ' '.join(split_command[1:])

                    # Save the currently open show to the Shows folder
                    self.__data.save_show(fr'Shows/{folderName}')

                # Else if the command starts with /open
                elif split_command[0] == '/open':

                    # Get the command's second word
                    secondWord = split_command[1]

                    # Get the rest of the command as a string, which should be the folder name
                    folderName = ' '.join(split_command[2:])

                    # If the command's second word is saved
                    if secondWord == 'saved':

                        # Try to open the saved show
                        self.__data.open_show(fr'Shows/{folderName}')

                    # Else if the command's second word is example
                    elif secondWord == 'example':

                        # Try to open the example show
                        self.__data.open_show(fr'Examples/{folderName}', False, 'example show was not found')

                # Else if the command is only one word
                elif len(split_command) == 1:

                    # Get the command
                    word_command = split_command[0]

                    # If the command is /list
                    if word_command == '/list':

                        # Format and set the display text to the dictionary of commands
                        commands = 'Commands: ' + '; '.join([f'{key} {self.__data.commandsDict[key]}' for key in self.__data.commandsDict])
                        self.__set_command_line_text(commands)

                    # Else if the command is /reset
                    elif word_command == '/reset':

                        # Reset the dataframes
                        self.__data.reset_data()

        # Catch an InvalidCommandInput exception
        except InvalidCommandInput as exception:

            # Display the error on the command line edit
            self.__set_command_line_text(f'Input Error: {exception.args[0]}')

        except FormatWarning as warning:
            # Let the user know that the file was not formatted correctly with a warning
            self.__mainWindow.formatWarningDialog(*warning.args)

        except FormatError as error:
            # Let the user know that the file was not formatted correctly with a warning
            self.__mainWindow.formatErrorDialog(*error.args)

        except Exception:
            # Display that a format error occurred on the command line edit
            self.__set_command_line_text('Format Error: the your command was invalidly formatted.')

        # Finally, update the GUI
        finally:
            self.__update_GUI()


    # Define the __update_dataframe to try to update one of the user dataframes
    def __update_dataframe(self, name:str, dataframe:pd.DataFrame):
        """Try to update one of the user dataframes."""

        try:

            # Format the all cues dataframe
            if name == 'All Cues':
                self.__data.format_all_cues(dataframe)

            # Format the attributes dataframe
            elif name == 'Attributes':
                self.__data.format_attributes(dataframe)

            # Format the states dataframe
            elif name == 'States':
                self.__data.format_states(dataframe)

        except FormatWarning as warning:
            # Let the user know that the file was not formatted correctly with a warning
            self.__mainWindow.formatWarningDialog(*warning.args)

        except FormatError as error:
            # Let the user know that the file was not formatted correctly with a warning
            self.__mainWindow.formatErrorDialog(*error.args)

        # Else, update the GUI to reflect the change
        else:
            self.__update_GUI()


    # Define the __run_GUI method to run the PyQt5 GUI
    async def __run_GUI(self):
        """Run the GUI forever."""
        # Wait for the setup tasks to finish
        await self.__setup_tasks

        # While the main window is not closed
        while not self.__mainWindow.closed:

            # Process events
            self.processEvents()

            # Sleep for 0 seconds
            await asyncio.sleep(0)

        # Else, raise a Stop exception
        else: raise Stop

# Define the main function
def main():
    # Create an instance of the server class
    cueServer = Server(r'attributes', r'all_cues', r'states', r'current_cues',
    r'nodes', r'cue_num', r'errors.json', {'/list': '(Display this list of commands)',
    '/goto cue [#]':'(Go directly to a cue group number)',
    '/save [name]':'(Save the currently opened show to the Shows folder)',
    '/open example [name]':'(Open an example of a show located in the Examples folder)',
    '/open saved [name]':'(Open a saved show located in the Shows folder)',
    '/reset':'(Reset back to the initial dataframes)'})

    # Run all the node's tasks simultaneously using asyncio
    asyncio.run(cueServer.run_tasks())


# When the program runs
if __name__ == '__main__':

    # Call the main() function
    main()