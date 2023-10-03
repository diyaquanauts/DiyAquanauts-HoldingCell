def subtractElements(sourceArray, targetArray):
    # Convert arrays to sets
    set1 = set(sourceArray)
    set2 = set(targetArray)

    # Find elements that are in set1 but not in set2
    missingElements = set1 - set2

    # Convert the missing elements set back to a list and return it
    return list(missingElements)

def subtractSuccessiveArrays(arrayList, startFromLast=False):
    # Determine the initial result based on the chosen starting point
    if startFromLast:
        result = arrayList[-1]
        arrays_to_subtract = arrayList[:-1]
    else:
        result = arrayList[0]
        arrays_to_subtract = arrayList[1:]

    # Iterate through the arrays to subtract
    for targetArray in arrays_to_subtract:
        result = subtractElements(result, targetArray)

    return result

# Example usage:
arrayList = [
    [1, 2, 32, 4, 5, 10],  # sourceArray 1
    [1, 2, 3, 41, 7],  # targetArray 1
    [2, 4, 6, 10],        # targetArray 2
    [1, 3, 5, 19]         # targetArray 3
]

finalResult = subtractSuccessiveArrays(arrayList)
print("Final Result:", finalResult)

finalResultLast = subtractSuccessiveArrays(arrayList, startFromLast=True)
print("Final Result (Starting from Last):", finalResultLast)
