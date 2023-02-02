import os

class FileWriter:
    def __init__(self, file_name, auto_overwrite=True, log_level=1):
        self.file_path = file_name
        self.auto_overwrite = auto_overwrite
        self.log_level = log_level

        scraped_dir = os.path.join(os.getcwd(), 'scraped')
        if not os.path.exists(scraped_dir):
            os.mkdir(scraped_dir)
        self.file_path = os.path.join(scraped_dir, self.file_path)

    def write_to_file(self, text):
        file_path_exists = os.path.exists(self.file_path)
        if file_path_exists:
            if self.log_level > 1:
                print(f"File {self.file_path} already exists.", end=' ')
            if not self.auto_overwrite:
                confirm = input(f"Do you want to overwrite it? (y/n)")
                if confirm.lower() != 'y':
                    return
            else:
                if self.log_level > 1:
                    print("Overwriting...")

        backup_file_path = None
        if file_path_exists:
            if self.log_level > 1:
                print(f"Creating backup file {self.file_path}.bak...")
            backup_file_path = self.file_path + ".bak"
            os.rename(self.file_path, backup_file_path)
            if self.log_level > 1:
                print(f"Backup file created.")

        try:
            if self.log_level > 1:
                print(f"Writing file {self.file_path}...")
            with open(self.file_path, 'w', encoding="utf-8") as file:
                file.write(text)
                if self.log_level > 0:
                    print(f"Written successfully.")
        except Exception as e:
            if self.log_level > 1:
                print(f"Error: {e}")
            if backup_file_path:
                os.rename(backup_file_path, self.file_path)
                if self.log_level > 0:
                    print(f"File restored from backup.")
            else:
                os.remove(self.file_path)
            raise
        finally:
            if backup_file_path:
                os.remove(backup_file_path)
                if self.log_level > 1:
                    print(f"Backup file removed.")

    def save(self, elements):
        output:str
        if isinstance(elements, str):
            output = elements
        elif isinstance(elements, list):
            if len(elements) == 0:
                output = ""
            if isinstance(elements[0], str):
                output = "\n".join(elements)
            else:
                output = "\n".join([str(element) for element in elements])
        
        self.write_to_file(output)