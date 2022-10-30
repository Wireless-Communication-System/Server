"""
Server Data Management classes that handle most of the data
"""

# Import pandas to work with pandas dataframes
import pandas as pd

# From numpy import nan for handling missing values
from numpy import nan

# Import the base data management classes
from Dependencies.DataManagement.Base import DataframeManager, IntManager

# Import the custom exceptions
from Dependencies.errors import FormatCheckWarning, FormatError, FormatCheckError, FormatWarning, InvalidCommandInput

# Import makedirs from os in order to create a folder for saved shows
from os import makedirs

# Define the UserDataframeManager child class of DataframeManager to manage user dataframes
class UserDataframeManager(DataframeManager):
    """Make, edit, get, and manage a user dataframe."""
    def __init__(self, filename:str, name:str, templateFileFormat:str=r'Templates/{filename}.csv') -> None:
        super().__init__(filename)

        # Store the name so the template can be formatted properly
        self.name = name

        # Format the filename to the directory where the template.csvs are stored and store it in a data attribute
        self.__templateFilename = templateFileFormat.format(filename=self.filename)

        # Try to get the template dataframe from file
        self.__template_open()

        # If the data dataframe is a blank dataframe
        if self.get_data().empty:

            # Set the data dataframe to the template dataframe
            self.update_data(self.__templateFrame)


    # Define the __template_open method to get the template pandas object
    def __template_open(self, mode:str='r') -> None:
        """Read and write to the csv file with the data pandas dataframe."""

        # If mode is equal to read, then read the contents of the template file
        if mode == 'r':

            # Try to read the csv file
            try:

                # Load the contents of the file into a pandas object
                pandasObject = pd.read_csv(self.__templateFilename, index_col=0)

                # If it is the all cues template, then format the index properly
                if self.name == 'All Cues':

                    # Reset the index of the dataframe and set the index to both the Cue Group Number and the Cue Number
                    pandasObject = pandasObject.reset_index().set_index(['Cue Group Number', 'Cue Number'])

            # Catch an exception if the file does not exist
            except (OSError, IOError, EOFError):

                # Set the pandas object to an empty dataframe
                pandasObject = pd.DataFrame()

            # Finally, set the template dataframe to the pandas object
            finally:

                # Set the data attribute to the pandas object
                self.__templateFrame = pandasObject

        # Else if mode is equal to write, then dump the template into its data file
        elif mode == 'w':

            # Dump the pandas object into its file
            self.__templateFrame.to_csv(self.__templateFilename)


    # Define the get method to get the pandas template dataframe
    def get_template(self) -> pd.DataFrame:
        """Get the pandas template dataframe."""

        # Return a copy of the dataframe
        return self.__templateFrame.copy()


    # Define the update method to update the pandas template dataframe
    def update_template(self, dataframe:pd.DataFrame):
        """Update the pandas template dataframe."""

        # Update the template dataframe data attribute
        self.__templateFrame = dataframe

        # Save it to its file
        self.__template_open('w')


    # Define the get file method to get the file location of the template
    def get_template_file(self) -> str:
        """Get the file location where the template dataframe is stored."""
        return self.__templateFilename

    
    # Define the saved_open method to try to open a saved dataframe file
    def saved_open(self, fileFormat:str) -> pd.DataFrame:
        """Try to open a saved dataframe file and get its dataframe."""

        # Try to read the csv file
        try:
            
			# Format the file's path
            filepath = fileFormat.format(filename=self.filename)

            # Load the contents of the file into a pandas object
            pandasObject = pd.read_csv(filepath, index_col=0)
                
        # Catch an exception if the file does not exist
        except (OSError, IOError, EOFError, FileNotFoundError):

            # Raise a FileNotFoundError
            raise FileNotFoundError

        # Else, return the pandas object
        else:
            return pandasObject


    # Define the save_frame method to try to save the dataframe to a csv file
    def save_frame(self, fileFormat:str) -> None:
        """Try to save the dataframe to a csv file."""
            
        # Format the file's path
        filepath = fileFormat.format(filename=self.filename)

        # Load the contents of the file into a pandas object
        self.get_data().to_csv(filepath)


# Define the ServerDataManagement class to manage each dataframe and perform operations between the dataframes for the server
class ServerDataManagement():
    """Manages each dataframe and perform operations between the dataframes on the server."""
    def __init__(self, attributesFile:str, allCuesFile:str, statesFile:str, currentCuesFile:str, nodesFile:str, cueNumFile:str, commandsDict:dict) -> None:
        # Create UserDataframeManager objects for the user files
        self.attributes = UserDataframeManager(attributesFile, 'Attributes')
        self.allCues = UserDataframeManager(allCuesFile, 'All Cues')
        self.states = UserDataframeManager(statesFile, 'States')

        # Create DataframeManager objects for the non-user files
        self.currentCues = DataframeManager(currentCuesFile)
        self.nodes = DataframeManager(nodesFile)

        # Create IntManager objects for the non-dataframe files
        self.cueNum = IntManager(cueNumFile)

        # Store the commands dictionary in a data attribute
        self.commandsDict = commandsDict

        # Update the maximum cue group
        self.update_max_cue_group()

        # Format and update the current cue dataframe
        self.format_current_cues()


    # Define the update_max_cue_group method to determine the max cue group
    def update_max_cue_group(self) -> None:
        """Update the maximum cue group number of the all cues frame."""
        self.maxCueGroup = self.allCues.get_data().reset_index().loc[:, 'Cue Group Number'].max()


    # Define the get_main_window_args method to return a list of the required arguments to create the main window
    def get_main_window_args(self) -> list:
        """Get a list of the required arguments to create the main window."""

        # Use list comprehension to get the filenames
        filenames = [dataframe.get_data_file() for dataframe in (self.attributes, self.allCues, self.states, self.currentCues, self.nodes)]

        # Return the current cue number, the filenames, and the commands dictionary
        return [int(self.cueNum)] + filenames + [self.commandsDict]


    # Define the __get_prefix method to determine if a cue number has a cue prefix
    def __get_prefix(self, cueNum:str) -> None:
        """Determine the prefix when formatting inputted cues, and raise a FormatCheckError if there is a problem."""

        # Remove the numbers from the prefix
        potentialPrefix = ''.join([char for char in cueNum if not(char.isdigit()) and char != '.'])

        # Get the prefix that is equal to the potentialPrefix
        prefix = [prefix for prefix in self.attributes.get_data().loc[:, 'Cue Prefix'] if prefix == potentialPrefix]

        # If only one prefix was found, then return that prefix
        if len(prefix) == 1:
            return prefix[0]

        # Else if the cue number is the last row storage, then return a numpy missing value
        elif cueNum == 'last_row_storage':
            return nan

        # Else, if no prefixes were found or multiple were found, raise a FormatCheckError exception
        else:
            raise FormatCheckError(f'cue prefix ({cueNum})', ' and you should make sure you assigned a node the prefix in the attributes sheet.')


     # Define the previous_cue method to go back a cue group
    def previous_cue(self) -> None:
        """Go to the previous cue group."""

        # Go to the last cue group if the current cue group is the first one
        if self.cueNum == 0:
            self.cueNum.update(self.maxCueGroup)
        else:
            self.cueNum -= 1

        # Update the current cues dataframe based on the cue number
        self.format_current_cues()


    # Define the next_cue method to go to the next cue group
    def next_cue(self) -> None:
        """Advance to the next cue group."""

        # Go back to the first cue group if the current cue group is the last one
        if int(self.cueNum) == self.maxCueGroup:
            self.cueNum.update(0)
        else:
            self.cueNum += 1

        # Update the current cues dataframe based on the cue number
        self.format_current_cues()


    # Define the warp_cue method to instantly warp to a given cue number
    def warp_cue(self, cueNum:int=0) -> None:
        """Go to a cue group based on its number."""

        # If the cue number is in the range of the cues numbers
        if cueNum >= 0 and cueNum <= self.maxCueGroup:

            # Update the cue number
            self.cueNum.update(cueNum)

            # Update the current cues dataframe based on the cue number
            self.format_current_cues()

            # Return True
            return True

        # Else, return False
        else: return False


    def format_attributes(self, dataframe:pd.DataFrame) -> None:
        """Format the attributes dataframe based on user inputted data."""

        try:
            # Check the column names
            self.__check_columns_names(dataframe, ['MAC Address', 'Node Number', 'Node Name', 'Cue Prefix'])

        # Catch any formatting warnings
        except FormatCheckWarning as warning:

            # Update the dataframe regardless
            self.attributes.update_data(dataframe)

            # Add the name of the dataframe and raise the warning to display a dialog
            raise FormatWarning('attributes', *warning.args)

        # Catch any formatting errors
        except FormatCheckError as error:

            # Add the name of the dataframe and raise the error to display a dialog
            raise FormatError('attributes', *error.args)

        # Else, update the dataframe with the inputted dataframe
        else:
            self.attributes.update_data(dataframe)


    def format_all_cues(self, dataframe:pd.DataFrame, formatted:bool=False) -> None:
        """Format the all cues dataframe based on user inputted data."""

        # Try to format the dataframe
        try:

            # If the dataframe is unformatted
            if not formatted:

                # Check the column names
                self.__check_columns_names(dataframe, ['Cue Number', 'When', 'Action', 'Cue State'])

                # Add a row to the dataframe to store the last row of data when the data is shifted
                dataframe.loc['last_row_storage'] = nan

                # Shift the dataframe down one
                dataframe = dataframe.shift()

                # Make the index a column to prevent loss of cue rows below empty rows
                dataframe.reset_index(inplace=True)

                # Drop all the rows that are completely empty
                dataframe.dropna(how='all', inplace=True)

                # Get the index values of the frame that are currently a column
                indexValues = dataframe.loc[:, 'Cue Number']

                # Set the starting group number to 0
                groupNum = 0

                # Set the group column to an empty list
                group_column = []

                # Set the prefix column to a list with a numpy missing value so the data lines up
                prefix_column = [nan]

                # For index in the index values of the dataframe
                for index in indexValues:

                    # If the index is a missing value, then add one to the group number and a missing value to the prefix column
                    if pd.isna(index):
                        groupNum += 1
                        prefix_column.append(nan)

                    # Else, get the cue prefix of the cue number and add it to the prefix column
                    else:
                        prefix_column.append(self.__get_prefix(index))

                    # Append the group number to the group column
                    group_column.append(groupNum)

                # Add the columns to the dataframe
                dataframe.loc[:, 'Cue Group Number'] = group_column
                dataframe.loc[:, 'Cue Prefix'] = prefix_column[:-1]

                # Move the Cue Prefix to the front
                dataframe = dataframe.set_index('Cue Prefix').reset_index()

                # Set the index to both the Cue Group Number and the Cue Number
                dataframe = dataframe.set_index(['Cue Group Number', 'Cue Number'])

                # Shift the dataframe back up
                dataframe = dataframe.shift(-1)

                # Remove the missing values from the dataframe
                dataframe.dropna(inplace=True)
            
            # Else, if it is formatted, then format the index properly
            else:

                # Reset the index of the dataframe and set the index to both the Cue Group Number and the Cue Number
                dataframe = dataframe.reset_index().set_index(['Cue Group Number', 'Cue Number'])

            # Determine if the column names are correct once formatted
            self.__check_columns_names(dataframe, ['Cue Group Number', 'Cue Number', 'Cue Prefix', 'When', 'Action', 'Cue State'])

            # Get the possible cue states from the states dataframe
            possible_cue_states = tuple(self.states.get_data().index)

            # If any of the cue states are not named correctly, raise a FormatCheckError for the cue states
            if any([True for state in dataframe.loc[:, 'Cue State'] if state not in possible_cue_states]):
                raise FormatCheckError('cue states', '. Make sure the cue states you entered for this sheet match the cue states in the states sheet.')

        # Catch any formatting warnings
        except FormatCheckWarning as warning:

            # Update the dataframe regardless
            self.allCues.update_data(dataframe)

            # Add the name of the dataframe and raise the warning to display a dialog
            raise FormatWarning('all cues', *warning.args)

        # Catch any formatting errors
        except FormatCheckError as error:

            # Add the name of the dataframe and raise the error to display a dialog
            raise FormatError('all cues', *error.args)

        # Else, if no errors occurred
        else:
            # Update the dataframe with the inputted dataframe
            self.allCues.update_data(dataframe)

            # Update the max group
            self.update_max_cue_group()

            # Reset the current cue group number back to 0
            self.warp_cue(0)


    def format_states(self, dataframe:pd.DataFrame) -> None:
        """Format the states dataframe based on user inputted data."""

        try:
            # Check the column names
            self.__check_columns_names(dataframe, ['Cue State', 'Initial Node State', 'Final Node State'])

            # Try to format the

        # Catch any formatting warnings
        except FormatCheckWarning as warning:

            # Update the dataframe regardless
            self.states.update_data(dataframe)

            # Add the name of the dataframe and raise the warning to display a dialog
            raise FormatWarning('states', *warning.args)

        # Catch any formatting errors
        except FormatCheckError as error:

            # Add the name of the dataframe and raise the error to display a dialog
            raise FormatError('states', *error.args)

        # Else, update the dataframe with the inputted dataframe
        else:
            self.states.update_data(dataframe)


    # Used by format methods of user dataframes
    def __check_columns_names(self, dataframe:pd.DataFrame, column_names:list) -> None:
        """Check the formatting of the column names."""

        # Get the column names of the dataframe and sort them
        columns = list(dataframe.reset_index().columns)
        columns.sort()

        # Get a sorted version of the column names
        sorted_column_names = column_names.copy()
        sorted_column_names.sort()

        # If the columns are not named correctly, raise a FormatCheckError for the column titles
        if columns != sorted_column_names:
            raise FormatCheckError('column titles', f' because they do not consist of the following: {", ".join(column_names)}')


    def format_current_cues(self) -> None:
        """Format the current cue dataframe based on the current cue number."""

        # Get the dataframe for the current cue group
        currentFrame = self.allCues.get_data().loc[int(self.cueNum)]

        # Set the 'Cue Prefix' as the index of the dataframe
        currentFrame = currentFrame.reset_index().set_index('Cue Prefix')

        # Update the current cues dataframe
        self.currentCues.update_data(currentFrame)

        # Reset the nodes dataframe to match
        self.reset_nodes()


    # Define the format_nodes method to format the nodes dataframe based on the received node series
    def format_nodes(self, node_series_list:list) -> None:
        """Format the node dataframe based on the received node series."""

        # If the nodes series list is not None, then update the nodes frame
        if node_series_list != None:

            # Get the current nodes frame
            nodesFrame = self.nodes.get_data()

            # Get each series in the list
            for series in node_series_list:
                
                # Get the series' cue number
                cueNum = series['Cue Number']

                # If the cue number is in the node dataframe's index, then update the dataframe with the series
                if cueNum in nodesFrame.index:
                    nodesFrame.loc[cueNum] = series

            # Update the nodes dataframe
            self.nodes.update_data(nodesFrame)

            # Update the Last Updated column
            self.update_last_updated()


    # Define the update_last_updated method to update the Last Update column on the nodes dataframe
    def update_last_updated(self) -> None:
        """Format a timestamp into a time since last updated."""

        # Get the nodes dataframe
        nodesFrame = self.nodes.get_data()

        # Add timestamp
        nodesFrame['Last Updated'] = nodesFrame['Timestamp'].map(self.format_timestamp)

        # Update the nodes dataframe
        self.nodes.update_data(nodesFrame)


    # Define the format_timestamp method to format the timestamps to be the time since last updated
    def format_timestamp(self, timestamp:pd.Timestamp) -> str:
        """Format a timestamp into a time since last updated."""
        
        # If the timestamp inputted is a pandas Timestamp
        if type(timestamp) == pd.Timestamp:

            # Get the time difference between the current timestamp and the argument timestamp
            timedelta = pd.Timestamp.now() - timestamp

            # Get the total minutes from the timedelta
            totalMin = round(timedelta.total_seconds() / 60)

            # If the total minutes is less than or equal to 99 minutes, set time normally
            if totalMin <= 99:
                time = f'{totalMin} min'
            
            # Else, if total minutes is greater than 99 minutes, set time to that
            else:
                time = '>99 min'
            
            # Return the time
            return time
        
        # Else, return nan
        else: return nan


    # Define the reset_nodes method to reset the nodes dataframe back to its default
    def reset_nodes(self) -> None:
        """Reset the nodes dataframe to its empty default."""

        # Get the current cues dataframe and reset its index
        currentFrame = self.currentCues.get_data().reset_index()

        # Create a dataframe with the proper columns using the current frame data
        nodesFrame = pd.DataFrame(data=currentFrame,
        columns=['Cue Number', 'When', 'Action', 'Cue State', 'Node Number', 'Node State', 'Timestamp'])

        # Set the index to the Cue Number
        nodesFrame.set_index('Cue Number', inplace=True)

        # Update the nodes dataframe
        self.nodes.update_data(nodesFrame)


    # Define the format_data method to format multiple dataframes
    def format_data(self, attributes:pd.DataFrame=None, states:pd.DataFrame=None, all_cues:pd.DataFrame=None, allCuesFormatted:bool=True, nodes:list=None) -> None:
        """Format multiple dataframes."""
        if type(attributes) == pd.DataFrame: self.format_attributes(attributes)
        if type(states) == pd.DataFrame: self.format_states(states)
        if type(all_cues) == pd.DataFrame: self.format_all_cues(all_cues, allCuesFormatted)
        if type(nodes) == list: self.format_nodes(nodes)
        elif nodes == 'reset': self.reset_nodes()

    # Define the reset_data method to reset all the data to their default values
    def reset_data(self) -> None:
        """Reset all the data to their default values."""        
        self.format_data(
            *[frame.get_template() for frame in (self.attributes, self.states, self.allCues)],
            True, 'reset')


    # Define the open_show method to open a saved show
    def open_show(self, folderName:str, formatted:bool=True, exceptionMessage:str='show was not found') -> None:
        """Open a saved show stored in a folder."""

        # Create a file format for the location of the files for the show
        fileFormat = folderName + r'/{filename}.csv'

        # Try to open the files and format the dataframes
        try:
            self.format_data(*[frame.saved_open(fileFormat)
            for frame in (self.attributes, self.states, self.allCues)],
            formatted, 'reset')
            
        # Catch a FileNotFoundError if the folder inputted did not exist
        except FileNotFoundError:
            
            # Raise an InvalidCommandInput exception
            raise InvalidCommandInput(exceptionMessage)
    

     # Define the save_show method to save the current show to a folder
    def save_show(self, folderName:str) -> None:
        """Save the current show to a folder."""

        # Create the folder if it does not already exist
        makedirs(folderName, exist_ok=True)

        # Create a file format for the location of the files for the show
        fileFormat = folderName + r'/{filename}.csv'

        [frame.save_frame(fileFormat) for frame in (self.attributes, self.states, self.allCues)]