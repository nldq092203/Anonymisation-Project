def replace_commas_with_tabs_in_place(file_path):
    """
    Replace all commas with tabs in the given file, modifying the file in place.

    :param file_path: Path to the file to be modified.
    """
    try:
        # Read the file content
        with open(file_path, 'r') as file:
            lines = file.readlines()

        # Replace commas with tabs
        modified_lines = [line.replace(',', '\t') for line in lines]

        # Write the modified content back to the same file
        with open(file_path, 'w') as file:
            file.writelines(modified_lines)

        print(f"File has been updated in place with commas replaced by tabs: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

# # Example usage
# if __name__ == "__main__":
#     file_path = './origin.csv'  # Replace with the path to your file
#     replace_commas_with_tabs_in_place(file_path)