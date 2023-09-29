import time
import sys
import os

def write_to_file(file_name, content):
    # Create the full file path by joining the current directory and the file name
    file_path = os.path.join(os.getcwd(), file_name)

    # Open the file in write mode, creating if it doesn't exist
    with open(file_path, 'a') as file:
        # Write the content to the file
        file.write(content)
def print_hello_world(phrase_to_print):
    output_file = "output_of_test_dot_py.txt"
    file_path = os.path.join(os.getcwd(), output_file)
    with open(file_path, "w") as file:
        file.write("\n" + "phrase_to_print1")
        while True:
            # print(f"{phrase_to_print}")
            file.write("\n" + "phrase_to_print")
            file.write("\n" +phrase_to_print)
            time.sleep(1)

if __name__=="__main__":
    # print("sys.argv")
    # print(sys.argv)
    # args1 = sys.argv[1:]  # Exclude the first argument, which is the script filename
    #
    # Print the arguments
    # print("Arguments:", args1)
    phrase_to_print = sys.argv[1]
    # phrase_to_print='hi people'
    print_hello_world(phrase_to_print)
