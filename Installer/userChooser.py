class userChooser:
    def showChoices(itemsToChoose, message="Enter the number corresponding to your choice: "):
        retVal = None

        keeyTrying = True

        while(keeyTrying):
            index = 0

            for choice in itemsToChoose:
                index = index + 1
                print(f"[{index}] {choice}")

            itemChoice = input(message)
            errMsg = "Invalid selection - please enter a valid number."

            try:
                itemChoice = int(itemChoice)
                if 1 <= itemChoice <= len(itemsToChoose):
                    retVal = itemsToChoose[itemChoice - 1]
                    keeyTrying = False
                else:
                    print(errMsg)
            except ValueError:
                print(errMsg)

        return retVal

if __name__ == "__main__":
    choices_list = ["Choice 1", "Choice 2", "Choice 3"]
    chosen_option = userChooser.showChoices(choices_list)
    print(f"You chose: {chosen_option}")
