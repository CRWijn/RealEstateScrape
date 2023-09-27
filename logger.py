from datetime import datetime

class CustomLogger:
    def __init__(self):
        self.max_entries = 100
        self.file_name = 'checks.log'

    def log(self, string_to_log):
        lines = []
        file_len = 0
        with open(self.file_name, 'a') as file: #Append the new log
            file.write(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + ' ' + string_to_log + '\n')
        with open(self.file_name, 'r') as file: #Get the file size and get ready to delete the first line
            lines = file.readlines()
            file_len = len(lines)
        if file_len > self.max_entries: #Delete first line
            with open(self.file_name, 'w') as file:
                for line in lines[1:]:
                    file.write(line)


#Quick test
if __name__ == '__main__':
    logger = CustomLogger()
    logger.max_entries = 5
    logger.log('Have')
    logger.log('A')
    logger.log('Nice')
    logger.log('Day')
    logger.log('And')
    logger.log('Never')
    logger.log('Sleep')
            
            
