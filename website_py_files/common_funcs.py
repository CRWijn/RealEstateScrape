def trunc_addr(address):
    addr_list = address.split(' ')
    for i, addr in enumerate(addr_list):
        try:
            int(addr)
            new_addr = ''
            for j in range(i+1):
                new_addr += addr_list[j] + ' '
            return new_addr[:-1]
        except:
            continue
    return address

def init_tel_bot():
    try:
        with open('credentials.txt', 'r') as file:
            lines = file.readlines()
            user_id = lines[0].strip()
            token = lines[1].strip()
    except FileNotFoundError:
        print("Can't find file")
        return 'Create a credentials.txt file containing your id'
    except Exception as e:
        print("Reached exception, " + str(e))
        return 'Something wrong with the credentials file' + str(e)
    return (f'https://api.telegram.org/bot{token}', {"chat_id": user_id, "text": ""})

def read_listings(agency_name):
    print("Reading logged listings")
    checked_ids = []
    with open('checked_archive/' + agency_name + '.txt', 'r') as file:
        for line in file:
            checked_ids.append(line.strip())
    return checked_ids

def write_listings(file, listing_ids):
    for listing_id in listing_ids:
        file.write(listing_id + '\n')
    
    

def maps_to_std(time_string):
    time_lst = time_string.split(' ')
    time_std = 0
    try:
        if 'hr' in time_lst:
            time_std += int(time_lst[0])
        return time_std if len(time_lst) <= 2 else time_std + int(time_lst[-2])/60
    except IndexError:
        print("Invalid time")
        return 999999999
