import ast
import re

def isLike(target, source):
    return bool(re.match(target, source))

def parseIndexData(indexData):
    # Split the input data into lines
    lines = indexData.split('\n')

    # Initialize an empty dictionary to store the result
    resultDict = {}

    # Iterate through each line
    for line in lines:
        # Split each line into columns based on the "|" character
        columns = line.strip().split('|')

        # Check if there are at least two columns
        if len(columns) >= 2:
            # Extract the key (first column) and values (second column)
            key = columns[0].strip()
            values = ast.literal_eval(columns[1].strip())

            # Add the key-value pair to the dictionary
            resultDict[key] = values

    return resultDict

def cleanPattern(matchPattern):
    # matchPattern = re.escape(matchPattern)
    matchPattern = matchPattern.replace(".", "~~~")
    matchPattern = matchPattern.replace("*", ".*")
    matchPattern = matchPattern.replace("~~~", "\.")

    return matchPattern

def cleanPatterns(matchPatterns):
    cleanPatterns = []

    for pattern in matchPatterns:
        clean = cleanPattern(pattern)
        cleanPatterns.append(clean)

    return cleanPatterns

def subtractElements(sourceArray, targetArray):
    # Convert arrays to sets
    set1 = set(sourceArray)
    set2 = set(targetArray)

    # Find elements that are in set1 but not in set2
    missingElements = set1 - set2

    # Convert the missing elements set back to a list and return it
    return list(missingElements)

def applySubtractionSetFilter(arrayList, bottomToTop=False):
    # Determine the initial result based on the chosen starting point
    if bottomToTop:
        result = arrayList[-1]
        arrays_to_subtract = arrayList[:-1]
    else:
        result = arrayList[0]
        arrays_to_subtract = arrayList[1:]

    # Iterate through the arrays to subtract
    for targetArray in arrays_to_subtract:
        result = subtractElements(result, targetArray)

    return result

def applyUniqueSetFilter(arrays):
    if len(arrays) == 0:
        return None
    elif len(arrays) == 1:
        # If only one array is passed in, return it as is
        return arrays

    # Convert the first array to a set to initialize the result
    result = set(arrays[0])

    # Iterate through the remaining arrays and subtract them from the result
    for array in arrays[1:]:
        result -= set(array)

    # Convert the final result set back to a list and return it
    return list(result)

def find(searchCriteriaAsJson, indexData):
    # Extract the required criteria...
    matchPatterns = searchCriteriaAsJson["MatchPatterns"]
    filterType = searchCriteriaAsJson["FilterType"]
    recordSetSize = searchCriteriaAsJson["RecordSetSize"]

    # Clean and convert the matchPatterns to RegEx...
    matchPatterns = cleanPatterns(matchPatterns)

    # Initialize an empty dictionary to store matching results
    matches = []

    # Transform TQL statements to regex and parse the data
    # regexStatements = [transformTqlToRegex(tql) for tql in matchPatterns]
    # parsedIndexData = parseIndexData(indexData)
    parsedIndexData = indexData

    # Loop through each TQL statement and evaluate against parsed data
    for pattern in matchPatterns:
        for key, values in parsedIndexData.items():
            # Check if the regex matches the key (row identifier)
            if isLike(pattern, key):
                # Add the matching row to the matches dictionary
                # matches.append([ pattern, key, val ues ] )
                matches.append(values)

    if (filterType == "subtractionSet"):
        matches = applySubtractionSetFilter(matches, bottomToTop=False)
    elif (filterType == "subtractionSetReverse"):
        matches = applySubtractionSetFilter(matches, bottomToTop=True)
    elif (filterType == "uniqueSet"):
        matches = applyUniqueSetFilter(matches)
    else:
        matches = applySubtractionSetFilter(matches, bottomToTop=False)

    if (recordSetSize < 0):
        recordSet = {"storeId": matches[recordSetSize:]}
    elif (recordSetSize > 0):
        recordSet = {"storeId": matches[:recordSetSize]}
    else:
        recordSet = {"storeId": matches}

    return recordSet

def _test():
    # Example TQL statements and data string
    matchPatterns = [
        "(Actions.Stored=true)|(Actions.IoA=true)",
        "(Actions.SpaceSaver=true)&&(Actions.SpaceSaverError=true)"
    ]


    indexData = """
    Actions.Indexed=true|['abc','def','ghi','jkl','mno']
    Actions.Stored=true|['abc','def','ghi', 'jkl','mno']
    Actions.SpaceSaver=true|['abc','def','mno','jkl','zyx']
    Actions.SpaceSaverError=true|['zyx']
    Actions.IoA=true|['abc','def']
    """

    # Call the find method to search for matches
    matches = find(matchPatterns, indexData)

    # Print the matching results
    index = 1

    for match in matches:
        print(f"-- Match #{index} --")
        print(f"Pattern: {match}")
        index +=1
