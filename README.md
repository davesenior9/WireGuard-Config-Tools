
# WireGuard Server
#### Preface
This is a guide to establish a WireGuard VPN in a Hub and Spoke topology, using AWS as the Hub. The Spokes will have the ability to communicate with each other, via the Hub, and if required, the Spokes can have their LANs communicate across the VPN.
#### Create a Domain Name
As a VPN endpoint requires a destination to terminate, we need to specify an IP address or a Domain Name with our configuration, that is 'Publicly Accessible'. There are several variables that can complicate this such as ISP NAT Configurations, Availability Issues, Cost of a fixed 'Public IP', availability to the Internet (Public vs Private) etc. To remove complications, we will use a free AWS instance.

By default, and AWS instance will be allocated a Public IP on creation, however, this IP is not permanently allocated to that instance. Things such as reboots can cause an instance to 'release' the IP it was using, and be allocated a new one. This is problematic as a client device might be installed at a distant location, with a fixed IP address in its VPN Config. If the Server then changes that IP Address, the client will never be able to re-establish a connection, as it will have the old/stale address. This can be resolved using Dynamic Domain Name Services.

DDNS (when configure) will associate any given Public IP Address, with a preconfigured, Human Readable Domain Name (aka Fully Qualified Domain Name -- FQDN). To 'own' a domain name such as Google.com, costs money. We will use a free service, with the only caveat being that the domain must be renewed/claimed, every 30 days, otherwise it will be available for use again, by anyone in the world.

#### NO-IP DDNS

- https://www.noip.com/
- Create an account and create a logical Domain Name, that is easy to remember. TIP: It can be named to associated the name to the service it is providing. eg. a Home Camera VPN could be 'hcv.ddns.net' or 'hcvpn.ddns.net'.
- Take note of the credentials created for this account.

#### AWS

- Create AWS Account - https://aws.amazon.com/
- Navigate to Compute > EC2
- Launch Instance
	- Free Tier Micro is suitable for a WireGuard (WG) Pivot
	- Ensure it is a Ubuntu Instance, rather than a AWS Linux Instance.
	- Creating a Key Pair if you don't have one already
		- Download the Key Pair, (for OS, Linux, OpenSSH(PS) = .PEM) (for Putty = .PPK)
	- Select new Instance
		- Copy Public IP Address
		
	#### Accessing the Instance
	
- FOR PPK - Open Putty, Navigate to Connection > SSH > Auth and import your downloaded Key Pair
- FOR PEM - Using CLI, use string `ssh -i <KEY PAIR.PEM> ubuntu@<PUB IP>` eg. `ssh -i C:\Users\Demo\Downloads\DEMO.pem ubuntu@13.155.13.55`
- Once you have your keypair mapped, enter your public IP address you have just copied, and start the SSH Session. The login will be `ubuntu` and the password is not required, as you are using a 'public certificate' as your authentication method (An account can be made so that is password protected, however, this should be used with caution).
	
	#### Building the WireGuard Server
	
-  Once logged in`sudo apt update && sudo apt upgrade`
- Install WG and supporting packages `sudo apt install wireguard qrencode git`
- Clone the following GitHub Repo `git clone https://github.com/davesenior9/WireGuard-Config-Tools`
- Move to the WireGuard-Config-Tools directory `cd WireGuard-Config-Tools`, this should return a confirmatory message.
- Run WGServer.py to create the baseline required `sudo python3 WGServer.py`
- Update the ddns.txt file with your Domain Name, deleting the existing 'example.ddns.net' `sudo nano /etc/wireguard/ddns.txt`
	
	#### Associate the Domain Name with the AWS Instance
	
- Install ddclient to setup the software that will bind the Domain Name to the public IP of the AWS Instance `sudo apt install ddclient`
- Follow the prompts, entering your User and Password, selecting 'Web Based IP Discovery`, rather than 'Network Interface', then finally, your Domain Name.
	- !!! This can be problematic. Confirm status of ddclient, using `sudo service ddclient status` if the service is functioning, you should see `SUCCESS:  updating example.ddns.net: good: IP address set to 3.27.38.227` !!!
		- If you do not see the above message, complete the following:
			- modify the ddclient.conf file `sudo nano /etc/ddclient.conf`
			- ensure it has the following:
			- `protocol=dyndns2`
			  `use=web, web=checkip.dyndns.com`
		       `server=www.noip.com`
               `login=XXX`
               `password='XXX'`
               `example.ddns.net`
			- restart the service, `sudo service ddclient restart`
			- confirm status of ddclient `sudo service ddclient status` and check for success.
			- It make take multiple restarts for this to effect.
	- Enable ddclient on boot using `sudo systemctl enable ddclient`
	
#### Modify AWS Instance Firewall
- On the AWS Instance dashboard, navigate to Security, and select the 'security group' hyper link.
- Then select 'Edit inbound rules'
- Select 'Add rule' > Custom TCP, Port Range 41194, Description 'WG'
-  ##### NOTE: By default, the Ubuntu VM does not run a firewall, the online protection from the Internet is this web based firewall hosted on AWS. Use this with caution. Use UFW or IPTABLES on the Ubuntu VM for more granular security.

#### Enable Spoke to Spoke Communication
- Enter the following command `sudo sysctl -w net.ipv4.ip_forward=1`
#### Create WireGuard Client
- Run `sudo python3 WG-Client-Creator.py`
- Once the client is created, you need a method to move the client profile to the desired endpoint. This can be done on some devices such as Android/iPhone by scanning the QR Code (when prompted). For other devices like PCs/SBCs, you must copy the contents of the clients profile into a corresponding config file eg. on a RPi `/etc/wireguard/wg0.conf` or on a Windows 10 WireGuard application, Creating a Tunnel and dumping the text, or saving the content as a `client.conf` file and importing it. If you have the know-how, use an SFTP tool such as WinSCP or basic sftp CLI to retrieve the file.
- Client configs and keys are stored within their own folders at `/etc/wireguard/clients/clientX`
	       
