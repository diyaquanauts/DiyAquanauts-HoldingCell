import os

# Function to split classes into separate text files
def scriptSplitter(inputScript):
    # Read the input script as a text file
    with open(inputScript, 'r') as scriptFile:
        scriptText = scriptFile.read()

    # Create a directory to store the class files
    outputDir = 'classFiles'
    os.makedirs(outputDir, exist_ok=True)

    # Split the script into classes
    classBlocks = scriptText.split('\nclass ')

    # Iterate through class blocks and export each as a separate text file
    for classBlock in classBlocks[1:]:  # Skip the first empty block
        # Extract the class name
        className = classBlock.split('\n', 1)[0]
        className = className.strip(":")
        className = className.strip(":")

        # Create a new text file for the class
        classFilePath = os.path.join(outputDir, f'{className}.py')

        classBlock = f"class {classBlock}\n"

        with open(classFilePath, 'w') as classFile:
            print(classBlock)
            classFile.write(classBlock)

if __name__ == '__main__':
    inputScript = 'queryService.py'  # Replace with the path to your script
    scriptSplitter(inputScript)
