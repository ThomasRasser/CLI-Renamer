"""
This script creates a file from all files in the current directory.
The user is than able to edit this list with his texteditor of choice.
The script can than read the edited file and apply the changes
"""

import os
import re
import sys

from datetime import datetime
from prompt_toolkit import prompt

DEBUG = True


class CLIProgram:
    """
    This is the class for the full CLI program
    and all its functionality
    """

    __current_path = os.getcwd()  # path were the script was called from
    __cli_path = os.path.realpath(__file__)  # path of the script
    __cli_directory = os.path.dirname(__cli_path)  # directory of the script

    __datetime_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    __new_names_filename = f"new_names_{__datetime_str}.txt"
    __new_names_path = __current_path + "/" + __new_names_filename
    __old_names: list[str] = []
    __old_details: list[str] = []

    def __init__(self) -> None:

        # Check if script is not called inside one of its own directories
        if not DEBUG and self.__current_path.startswith(self.__cli_directory):
            print(
                "This script is not supposed to be called from within its own directory"
            )
            sys.exit()

        self.initialise_data_lists()
        if not self.create_new_names_file():
            self.exit_renamer(False)

    def remove_multiple_spaces(self, string: str) -> str:
        """
        Removes multiple spaces from a string
        """

        cleaned_string = re.sub(r"\s+", " ", string)
        return cleaned_string

    def initialise_data_lists(self) -> None:
        """
        Updates the current names and details list
        """

        self.__old_names = self.get_ls_output_list()
        self.__old_details = self.get_file_details_list()

    def set_back_to_default(self) -> None:
        """
        Sets the new names file back to the default
        and reinitialises the data lists
        """

        # We don't have to check, if the file already exists like in "create_new_names_file"
        # Since we can only get here once a new file is created at the initial start of the program
        # Therefore, there MUST exist a file and we can just write to it
        with open(self.__new_names_path, "w", encoding="utf-8") as temp_file:
            temp_file.write("\n".join(self.__old_names))

        self.initialise_data_lists()

        print("Reinitialised data")

    def get_ls_output_list(self) -> list[str]:
        """
        Returns the output of the ls command
        at the current directory
        """

        ls_output = os.popen("ls -1").read()

        # remove empty lines and convert to list[str]
        clean_ls_output_list = ls_output.split("\n")
        clean_ls_output_list = list(filter(None, clean_ls_output_list))
        clean_ls_output_list = list(map(str, clean_ls_output_list))
        clean_ls_output_list = list(
            map(self.remove_multiple_spaces, clean_ls_output_list)
        )

        # remove the new_names file if present
        for name in clean_ls_output_list:
            if self.__new_names_filename in name:
                clean_ls_output_list.remove(name)

        return clean_ls_output_list

    def get_file_details_list(self) -> str:
        """
        Returns detailed information about the files
        in the current directory
        """

        ls_output_detailed = os.popen("ls -l").read()

        # remove empty lines and convert to list[str]
        clean_ls_output_list = ls_output_detailed.split("\n")
        clean_ls_output_list = list(filter(None, clean_ls_output_list))
        clean_ls_output_list = list(map(str, clean_ls_output_list))
        clean_ls_output_list = list(
            map(self.remove_multiple_spaces, clean_ls_output_list)
        )

        # remove first line, since it only shows the total size
        clean_ls_output_list = clean_ls_output_list[1:]

        # remove the new_names file if present
        for name in clean_ls_output_list:
            if self.__new_names_filename in name:
                clean_ls_output_list.remove(name)

        return clean_ls_output_list

    def get_new_names_from_file(self) -> list[str]:
        """
        Returns the new names from the file
        as a list of strings
        """

        with open(self.__new_names_path, "r", encoding="utf-8") as temp_file:
            new_names = temp_file.read()
            new_names = new_names.split("\n")
            new_names_list = filter(None, new_names)
            new_names_list = list(map(str, new_names_list))

        return new_names_list

    def create_new_names_file(self) -> bool:
        """
        Creates a new_names file with the output of the ls command
        in the directory of the script
        """

        if os.path.exists(self.__new_names_path):
            print(f"The file already exists: {self.__new_names_path}")
            return False

        with open(self.__new_names_path, "w", encoding="utf-8") as temp_file:
            temp_file.write("\n".join(self.__old_names))

        return True

    def delete_new_names_file(self) -> None:
        """
        Deletes the temp file
        """

        # Check if the file exists
        if not os.path.exists(self.__new_names_path):
            print("The new_names file does not exist")
            return

        try:
            os.remove(self.__new_names_path)
        except Exception:
            print("Error deleting the new_names.txt file")

    def new_names_are_valid(self) -> bool:
        """
        Validates renaming is possible
        e.g. valid filenames, same number, ...
        And prints the error if one is found
        """

        # Compare details
        new_details = self.get_file_details_list()
        if self.__old_details != new_details:
            print("The files have changed")
            return False

        new_names = self.get_new_names_from_file()

        # Compare number of files
        if len(self.__old_names) > len(new_names):
            print("The number of files in the new_names file is to short")
            return False
        elif len(self.__old_names) < len(new_names):
            print("The number of files in the new_names file is to long")
            return False

        # Check for forbidden characters: <, >, :, ", /, \, |, ?, *
        forbidden_characters = ["<", ">", ":", '"', "/", "\\", "|", "?", "*"]
        for new_name in new_names:
            for char in forbidden_characters:
                if char in new_name:
                    print(f"Invalid character in filename: {char} -> {new_name}")
                    return False

        # Check for special characters: \n, \r, ...
        special_characters = ["\n", "\r", "\t", "\b", "\f", "\v", "\a"]
        for new_name in new_names:
            for char in special_characters:
                if char in new_name:
                    print(f"Special character in filename: {char}")
                    return False

        return True

    def show_new_filenames(self) -> None:
        """
        Prints the new filenames into the console
        """

        if not self.new_names_are_valid():
            return

        new_names = self.get_new_names_from_file()
        for new_name, old_name in zip(new_names, self.__old_names):
            if new_name != old_name:
                print(
                    f"\033[42m\033[30mNEW:\033[0m {new_name}"
                )  # Green background, black font
                print(
                    f"\033[41m\033[30mOLD:\033[0m {old_name}"
                )  # Red background, black font
            else:
                print(
                    f"\033[43m\033[30mNEW:\033[0m {new_name}"
                )  # Green background, black font

            if new_name != new_names[-1]:
                print()

    def open_texteditor(self, texteditor_command: str) -> None:
        """
        Opens the default texteditor with the new_names file
        """

        # Check if the file exists
        if not os.path.exists(self.__new_names_path):
            print("The new_names file does not exist")
            return

        # Fix the path to work for wsl and windows
        new_name_path = self.__new_names_path
        if "/mnt/c" in self.__new_names_path:
            new_name_path = f"C:{self.__new_names_path[6:]}"
        else:
            new_name_path = f"//wsl.localhost/Ubuntu{self.__new_names_path}"

        print(f"Opening {self.__new_names_filename} with {texteditor_command}")
        try:
            os.system(f"\"{texteditor_command}\" \"{new_name_path}\"")
        except Exception:
            print("Error opening the new_names.txt file")

    def rename_files(self) -> None:
        """
        Renames the files in the current directory
        """

        if not self.new_names_are_valid():
            return

        new_names = self.get_new_names_from_file()
        for new_name, old_name in zip(new_names, self.__old_names):
            if new_name != old_name:
                try:
                    os.rename(old_name, new_name)
                except Exception:
                    print(
                        f"\033[41m\033[30mERROR:\033[0m {old_name} -> {new_name}"
                    )  # Red background, black font

                print(
                    f"\033[42m\033[30mOK:\033[0m {old_name} -> {new_name}"
                )  # Green background, black font

    def exit_renamer(self, delete: bool) -> None:
        """
        Exits the program and deletes the new names file
        """

        if delete:
            self.delete_new_names_file()

        print("Exiting Renamer.")
        sys.exit()


if __name__ == "__main__":
    cli_program = CLIProgram()

    try:
        while True:
            command = prompt(
                "Enter command (d: back to default, p: preview, t: texteditor, r: rename, q: quit): "
            )
            print("----------------------------------------")
            if command == "d" or command == "d":
                cli_program.set_back_to_default()
            elif command == "preview" or command == "p":
                cli_program.show_new_filenames()
            elif command == "rename" or command == "r":
                cli_program.rename_files()
            elif command == "texteditor" or command == "t":
                cli_program.open_texteditor("subl.exe")
            elif command == "exit" or command == "q":
                cli_program.exit_renamer(True)
            else:
                print("Unknown command.")
            print("----------------------------------------")
    except KeyboardInterrupt:
        cli_program.exit_renamer(False)
