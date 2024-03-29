#!/usr/bin/python3
import os

try:
    ##CREATE INITIAL SERVER FILE
    cmd = os.system('mkdir /etc/wireguard/serverkeys')
    cmd = os.system('mkdir /etc/wireguard/clients')
    cmd = os.system('mkdir /etc/wireguard/clients/client1')
    cmd = os.system('touch /etc/wireguard/clients/client1/client.conf | echo "#Client1 = Server" > /etc/wireguard/clients/client1/client.conf')
    cmd = os.system('touch /etc/wireguard/ddns.txt')
    with open('/etc/wireguard/ddns.txt', 'w') as f:
        f.write('example.ddns.net:41194')
        f.close
    cmd = os.system('umask 077; wg genkey | tee /etc/wireguard/serverkeys/privatekey | wg pubkey > /etc/wireguard/serverkeys/publickey')

    with open('/etc/wireguard/serverkeys/privatekey', 'r') as f:
        private_key = f.read()
        private_key = str(private_key)

    with open('/etc/wireguard/serverkeys/publickey', 'r') as f:
        public_key = f.read()
        public_key = str(public_key)

    default_data = ['\n',('#VPN Server IP\n'), '[Interface]\n', ('Address = 192.168.100.1/24\n'), '\n', ('#VPN Server Port\n'), (f'ListenPort = 41194\n'), '\n', ('#VPN Server Private Key\n'), (f'PrivateKey = {private_key}\n'), '\n']
    with open(f'/etc/wireguard/wg0.conf', 'a') as f:
        f.writelines(default_data)
        f.close

    cmd = os.system('sudo systemctl enable wg-quick@wg0')
    cmd = os.system('sudo systemctl start wg-quick@wg0')

    ##ENABLE MASQURADE/NAT
    cmd = os.system('sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE')
    cmd = os.system('sudo iptables-save')

    print ('### WG Server Successfully Configured ###')

except Exception as error:
    print ("An exception was thrown! Are you sure you ran the script as root. Use 'sudo xxxx'")
    print (str(error))
