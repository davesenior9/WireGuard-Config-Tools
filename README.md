
# WireGuard Server
#### Create a Domain Name
As a VPN endpoint requires a destination to terminate, we need to specify an IP address or a Domain Name with our configuration, that is 'Publicly Accessible'. There are several variables that can complicate this such as ISP NAT Configurations, Availability Issues, Cost of a fixed 'Public IP', availability to the Internet (Public vs Private) etc. To remove complications, we will use a free AWS instance.

By default, and AWS instance will be allocated a Public IP on creation, however, this IP is not permanently allocated to that instance. Things such as reboots can cause an instance to 'release' the IP it was using, and be allocated a new one. This is problematic as a client device might be installed at a distant location, with a fixed IP address in its VPN Config. If the Server then changes that IP Address, the client will never be able to re-establish a connection, as it will have the old/stale address. This can be resolved using Dynamic Domain Name Services.

DDNS (when configure) will associate any given Public IP Address, with a preconfigured, Human Readable Domain Name (aka Fully Qualified Domain Name -- FQDN). To 'own' a domain name such as Google.com, costs money. We will use a free service, with the only caveat being that the domain must be renewed/claimed, every 30 days, otherwise it will be available for use again, by anyone in the world.

#### NO-IP DDNS
- https://www.noip.com/
#### AWS
- Create AWS Account - https://aws.amazon.com/
- Navigate to Compute > EC2
- Launch Instance
	- Free Tier Micro is suitable for a WireGuard (WG) Pivot
	- Ensure it is a Ubuntu Instance, rather than a AWS Linux Instance)
	- Creating a Key Pair if you don't have one already
		- Download the Key Pair, (for OS, Linux, OpenSSH(PS) = .PEM) (for Putty = .PPK)
	- Select new Instance
		- Copy Public IP Address
		
	#### Accessing the Instance
	- FOR PPK - Open Putty, Navigate to Connection > SSH > Auth and import your downloaded Key Pair
	- FOR PEM - Using CLI, use string `ssh -i <KEY PAIR.PEM> ubuntu@<PUB IP>` eg. `ssh -i C:\Users\Demo\Downloads\DEMO.pem ubuntu@13.155.13.55`
	
	-  Once logged in`sudo apt update && sudo apt upgrade`
	- Install WG and supporting packages `sudo apt install wireguard qrencode git`
	- Clone the following GitHub Repo `git clone https://github.com/davesenior9/WireGuard-Config-Tools`

