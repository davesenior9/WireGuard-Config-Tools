#!/usr/bin/python3
import os

client_number = 0

def existing_clients():
    print ('\nExisting Clients\n')
    peer_info = []
    client_dir = os.listdir('/etc/wireguard/clients/')
    client_dir.sort()
    for client in client_dir:
        try:
            f = open(f'/etc/wireguard/clients/{client}/client.conf', 'r')
            client_data = f.readlines()
            for line in client_data:
                if '#' == line[0]:
                    line = line.strip('#'); line = line.strip()
                    peer_info.append(line)
                if 'Address' in line:
                    line = line.split('='); line = line[1].split('/')
                    peer_info.append(line[0].strip())
        except Exception:
            print ('Found Client with no Description or No Client Config')
    for line in peer_info:
        print (line)
    return

def client_input_func():
    global client_number
    print ('\nCLIENT 1 IS ALLOCATED TO THE SERVER, DO NOT ENTER "1"\n')
    client_number = int(input('What is the Client Number?\n'))
    if type(client_number) != int or client_number <= 1:
        raise Exception("Incorrect Client Number")
    description = input('What is the Description of the Client?\n')
    key_generate(client_number)
    user_generate(client_number, description)
    server_side(client_number, description)
    return 

def key_generate(client_number):
    cmd = os.system(f'mkdir /etc/wireguard/clients/client{client_number}')
    cmd = os.system(f'umask 077; wg genkey | tee /etc/wireguard/clients/client{client_number}/privatekey | wg pubkey > /etc/wireguard/clients/client{client_number}/publickey')

def user_generate(client_number, description):
    with open(f'/etc/wireguard/clients/client{client_number}/privatekey', 'r') as f:
        private_key = f.read()
        private_key = str(private_key)
    with open(f'/etc/wireguard/serverkeys/publickey', 'r') as f:
        srv_pub_key = f.read()
        srv_pub_key = str(srv_pub_key)
    with open(f'/etc/wireguard/ddns.txt', 'r') as f:
        ddns = f.read()
        ddns = str(ddns)
        if 'example' in ddns:
            print ('ERROR: UPDATE THE DDNS FILE')
            return
    default_data = [(f'#Client{client_number} = {description}\n'),'[Interface]\n', (f'PrivateKey = {private_key}'), (f'Address = 192.168.100.{client_number}/32\n'), ('DNS = 1.1.1.1\n'), '\n[Peer]\n', (f'PublicKey = {srv_pub_key}'), (f'AllowedIPs = 192.168.100.0/24\n'), (f'Endpoint = {ddns}'), (f'PersistentKeepalive = 15\n')]
    with open(f'/etc/wireguard/clients/client{client_number}/client.conf', 'w') as f:
        f.writelines(default_data)
        f.close

def server_side(client_number,description):
    with open(f'/etc/wireguard/clients/client{client_number}/publickey', 'r') as f:
        public_key = f.read()
        public_key = str(public_key)

    default_data = ['\n','[Peer]\n', (f'#{description}\n'), (f'AllowedIPs = 192.168.100.{client_number}/32\n'), (f'PublicKey = {public_key}\n')]
    with open(f'/etc/wireguard/wg0.conf', 'a') as f:
        f.writelines(default_data)
        f.close
    cmd = os.system('systemctl restart wg-quick@wg0')

def view_config():
    view_config = input(f'Do you want to view config of Client{client_number}?(y/n)\n')
    if view_config == 'y': 
        f = open(f'/etc/wireguard/clients/client{client_number}/client.conf')
        f = f.read()
        print (f)
    return

def qr_code_generate():
    qr_code = input('Do you want to generate a QR Code of the config?(y/n)\n')
    if qr_code == 'y':
        cmd = os.system(f'qrencode -t ansiutf8 < /etc/wireguard/clients/client{client_number}/client.conf')
    elif qr_code == 'n':
            pass
    else:
        print (f'You entered {qr_code}. Enter "y" or "n"\n')
    return

def remove_client():
    f = open('/etc/wireguard/wg0.conf', 'r')
    data = f.readlines()
    f.close()
    if (input('\nDo you want to remove a Client?(y/n)\n')) == 'y':
        while True:
            try:
                desc = ''
                existing_clients()
                client_removal = int(input('\nEnter the Client number that you want to remove.\n'))
                if type(client_removal) != int or client_removal <= 1:
                    raise Exception("Incorrect Client Number")
                client = open(f'/etc/wireguard/clients/client{client_removal}/client.conf', 'r')
                cmd = os.system(f'rm -r /etc/wireguard/clients/client{client_removal}')
                client_data = client.readlines()
                for line in client_data:
                    if 'Client' in line:
                        desc = line.split('=')[1]
                        desc = desc.strip()
                        desc = ('#' + desc + '\n')
    
                if desc in data:
                    desc_index = data.index(desc)
                    if 'PersistentKeepalive' in (data[desc_index + 3]): 
                        del data[(desc_index - 1):(desc_index + 6)]
                    else:
                        del data[(desc_index - 1):(desc_index + 5)]
                    f = open('/etc/wireguard/wg0.conf', 'w')
                    f.writelines(data)
                    f.close()
                    cmd = os.system('systemctl restart wg-quick@wg0')
                if (input('\nDo you want to delete another?(y/n)') != 'y'):
                    return
            except Exception as e:
                print (f'An Error has occured {e}')
            return

while True:
    try:
        if (input('\nDo you want to create a Client?(y/n)\n')) == 'y':
            while True:
                existing_clients()
                client_input_func()
                qr_code_generate()
                view_config()
                restart = input('Do you want to make another Client?(y/n)\n')
                if restart == 'y':
                    pass
                else:
                    break
        remove_client()
        break
    except KeyboardInterrupt or Exception as e:
        print (f'\nError: {e}')
        break
