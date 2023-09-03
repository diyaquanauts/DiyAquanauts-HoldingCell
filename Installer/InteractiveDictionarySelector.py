import os
import platform


class WorkflowSelector:
    def __init__(self, table):
        self.table = table


    def clear_screen(self):
        try:
            if platform.system() == "Windows":
                os.system('cls')
            else:
                os.system('clear')
        except:
            pass

    def display_table(self):
        for i, row in enumerate(self.table):
            if row[0] == True:
                include = "[ X ]"
            else:
                include = "[   ]"
            print(f"{i + 1}. {include} {row[1]}")
            i = i + 1

    def selectWorkflow(self, customMsg = ""):

        while True:
            self.clear_screen()
            self.display_table()
            print()
            print("Are the selected items acceptable?")
            print()
            if(len(customMsg) > 0):
                print(customMsg)
                print()
            user_input = input("To change the selection state of an item, type the number and hit enter. Otherwise, hit enter to continue... ")

            if user_input.isdigit():
                index = int(user_input) - 1
                if 0 <= index < len(self.table):
                    table[index][0] ^= table[index][0]
            elif user_input.strip() == "":
                break

        return self.table

# Example usage:
if __name__ == "__main__":
    table = [
        [True, "Description One", "Code One"],
        [True, "Description Two", "Code Two"],
        [True, "Description Three", "Code Three"],
        [True, "Description Four", "Code One"],
        [True, "Description Five", "Code Two"],
        [True, "Description Six", "Code Three"],
        [True, "Description Seven", "Code One"],
        [True, "Description Eight", "Code Two"],
        [True, "Description Nine", "Code Three"],
        [True, "Description Ten", "Code One"],
        [True, "Description Eleven", "Code Two"],
        [True, "Description Twelve", "Code Three"]
        ]

    selector = WorkflowSelector(table)
    result_table = selector.selectWorkflow("If you have not run the installer script before, it is *highly* recommened that you leave all the values above at their defaults...")

    # Display the resulting table
    print("Resulting Table:")
    for row in result_table:
        print(row)
