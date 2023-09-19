class Website:
    def __init__(self, url, execution_func):
        self.url = url
        self.exec_func = execution_func

    def execute_search(self):
        self.exec_func(self.url)

    @staticmethod
    def funda(url):
        print(url)
    
    
        
def read_websites():
    websites = {}
    with open('website_list.txt', 'r') as file:
        for line in file:
            line = line.split(' ')
            websites[line[0]] = line[1]
    return websites
