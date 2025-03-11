# Takes a pandas series and returns a dictionary mapping a number to each value in the array
def createIdMap(series):
    id_mapping = {}

    # Loop through elements and include an index
    for index, element in enumerate(series):
        id_mapping[element] = index + 1001  # Assign element to a unique number
    
    return id_mapping

# Returns a dataframe with real ids turned to temp ids
def useMapEncode(df, dict):
    new_df = df.copy()

    new_df['id'] = new_df['id'].map(dict)
    
    return new_df

# Returns a dataframe with temp ids turned back into real ids
def useMapDecode(df, dict):
    new_df = df.copy()

    # Invert the mapping to have the opposite function of useMapEncode()
    inverted_mapping = {v: k for k, v in dict.items()}
    
    new_df['id'] = new_df['id'].map(inverted_mapping)

    return new_df