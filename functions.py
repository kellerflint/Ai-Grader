import re

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

# Return an array including all indexes with questions
def findQuestionIndexes(df):
    # Regex pattern to match question columns (numeric ID followed by a colon)
    question_pattern = r"^\d+: .+"

    question_column_indexes = []

    # Iterate through the DataFrame columns to find the question columns
    for index, col in enumerate(df.columns):
        if re.match(question_pattern, col):
            question_column_indexes.append(index)

    return question_column_indexes

def splitDfByQuestion(df, questionIndex):
    new_df = df[['id', df.columns[questionIndex]]]
    return new_df