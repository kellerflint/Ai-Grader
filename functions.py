#takes a pandas series and returns a dictionary mapping a number to each value in the array
def createIdMap(series):
    id_mapping = {}

    # Loop through elements and include an index
    for index, element in enumerate(series):
        id_mapping[index + 1] = element  # Assign element to a unique number
    
    return id_mapping