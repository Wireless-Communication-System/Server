"""
Base Data Management classes that handle most of the data
"""

# Import pandas to work with pandas dataframes
import pandas as pd

# From the pickle module import dump and load to work with pickle data
from pickle import dump, load

# Define the IntManager class to make, edit, get, and manage integer pickle data
class IntManager():
    """Make, edit, get, and manage integer pickle data."""
    def __init__(self, filename:str) -> None: 

        # Format the filename to the directory where the actual data is stored
        self.__dataFilename = fr'Data/{filename}.dat'

        # Try to get the data from file
        self.__data_pickle()


    # Define the __data_pickle method to load from or dump to the pickle file with the data
    def __data_pickle(self, mode:str='rb') -> None:
        """Read and write to the data pickle file with the data."""

        # Try to open the pickle file
        try:

            # Open the node number file for either read or write binary
            with open(self.__dataFilename, mode) as fileObject:

                # If mode is equal to read binary, then load the contents of the file
                if mode == 'rb':

                    # Load the contents of the file into the data attribute
                    self.__data = load(fileObject)
                
                # Else if mode is equal to write binary, 
                # then dump the data attribute into the file
                elif mode == 'wb':

                    # Dump the data into the file
                    dump(self.__data, fileObject)

        # Catch an exception if the file does not exist
        except (OSError, IOError, EOFError):

            # Set the data attribute to 0
            self.__data = 0


    # Define the update method to update the data
    def update(self, data) -> None:
        """Update the data."""

        # Update the pickle data stored in the data attribute
        self.__data = data

        # Save it to its file
        self.__data_pickle('wb')


    # Define the get file method to get the file location of the data
    def get_file(self) -> str:
        """Get the file location where the data is stored."""
        return self.__dataFilename
    

    # Define the __iadd__ method so that += can be used
    def __iadd__(self, other):
        
        # Increase the integer by other
        self.__data += other

        # Save it to its file
        self.__data_pickle('wb')

        # Return self
        return self

    
     # Define the __isub__ method so that -= can be used
    def __isub__(self, other):
        
        # Decrease the integer by other
        self.__data -= other

        # Save it to its file
        self.__data_pickle('wb')

        # Return self
        return self


    # Define the __str__ method so that it can be represented as a string
    def __str__(self):
        return str(self.__data)


    # Define the __int__ method so that it can be represented as an int
    def __int__(self):
        return int(self.__data)


    # Define the __eq__ method so that == can be used    
    def __eq__(self, other):
        if self.__data == other: return True
        else: return False


# Define the DataframeManager class to make, edit, get, and manage a dataframe
class DataframeManager():
    """Make, edit, get, and manage a dataframe."""
    def __init__(self, filename:str, fileFormat:str=r'Data/{filename}.dat') -> None:
        # Store the generic filename in a data attribute
        self.filename = filename

        # Format the filename to the directory where the actual data is stored
        self.__dataFilename = fileFormat.format(filename=self.filename)

        # Try to get the data dataframe from file
        self.__data_pickle()


    # Define the __data_pickle method to load from or dump to the pickle file with the data pandas object
    def __data_pickle(self, mode:str='r') -> None:
        """Read and write to the data pickle file with the data pandas dataframe."""

        # If mode is equal to read, then read the contents of the data file
        if mode == 'r':

            # Try to unpickle the file
            try:

                # Load the contents of the file into a pandas object
                pandasObject = pd.read_pickle(self.__dataFilename)
            
            # Catch an exception if the file does not exist
            except (OSError, IOError, EOFError):

                # Set the pandas object to an empty dataframe
                pandasObject = pd.DataFrame()
                
            # Finally, set the data dataframe to the pandas object
            finally:

                # Set the data attribute to the pandas object
                self.__dataFrame = pandasObject

        # Else if mode is equal to write, then dump the data into its data file
        elif mode == 'w':

            # Dump the pandas object into its file
            self.__dataFrame.to_pickle(self.__dataFilename)
    

    # Define the get method to get the pandas data dataframe
    def get_data(self) -> pd.DataFrame:
        """Get the pandas dataframe."""

        # Return a copy of the dataframe
        return self.__dataFrame.copy()


    # Define the update method to update the pandas data dataframe
    def update_data(self, dataframe:pd.DataFrame) -> None:
        """Update the pandas dataframe."""

        # Update the data dataframe data attribute
        self.__dataFrame = dataframe

        # Save it to its file
        self.__data_pickle('w')


    # Define the get file method to get the file location of the data
    def get_data_file(self) -> str:
        """Get the file location where the data dataframe is stored."""
        return self.__dataFilename