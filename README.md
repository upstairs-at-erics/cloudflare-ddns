## Cloudflare DDNS Updater
A lightweight, container‑friendly Python script that automatically updates Cloudflare DNS A records to match your current public IP address.  
Perfect for home servers, Tailscale nodes, Proxmox hosts, or any environment where your WAN IP changes.  
This project is designed to run cleanly inside Docker, with environment‑driven configuration and optional Gotify notifications.  

### Features
• 	Updates multiple hostnames in a single run  
• 	Uses Cloudflare’s official API (v4)  
• 	Detects your public IP via api.ipfy.org  
• 	Sends Gotify notifications on update or error  
• 	Clean error handling for:
• 	invalid/missing API token  
• 	unreachable Cloudflare API  
• 	missing DNS records  
• 	Docker‑ready  
• 	Works perfectly with Portainer stack deployments  

### Project Structure
cloudflare-ddns/  
├── ddns-cloudflare.py      # Main script  
├── Dockerfile              # Container build  
├── stack-example.txt       # Example Portainer stack  
├── .env                    # Your environment keys for locally running (ignored by Git)   
└── stack.txt               # Your local stack (ignored by Git)  

### Environment Variables
The script is fully environment‑driven. 

CF_API_TOKEN=your_token_here  
CF_ZONE_NAME=example.com  
CF_HOSTS=home.example.com, vpn.example.com  
GOTIFY_URL=https://gotify.example.com  
GOTIFY_TOKEN=abc123  
GOTIFY_IF_UNCH=False  


### Running with Docker
Build the image:
'docker build -t cloudflare-ddns .'

Run it:
'docker run --env-file .env cloudflare-ddns'


### Portainer Stack Example
See stack-example.txt for a ready‑to‑use stack.
Basic structure:

services:  
  ddns:  
    image: cloudflare-ddns:latest  
    env_file:  
      - .env  
    restart: unless-stopped  



### Running Locally (without Docker)
Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install requests


Run the script:
'python ddns-cloudflare.py'

### Error Handling
The script gracefully handles:
• 	Missing or invalid Cloudflare token
• 	Cloudflare API timeouts
• 	Zone not found
• 	DNS record missing
• 	Network errors
• 	JSON parsing failures
All errors are printed and optionally sent to Gotify.

### Logging  
The script prints:  
• 	Current public IP  
• 	DNS records in the zone  
• 	Per‑hostname update status  
• 	Error messages when applicable  

### Future Enhancements  
• 	Support for AAAA (IPv6) records  
• 	Optional Cloudflare proxy toggle  
• 	Multi‑zone support  
• 	Scheduled cron‑style execution inside container  

### License  
MIT License — feel free to use, modify, and contribute.  










