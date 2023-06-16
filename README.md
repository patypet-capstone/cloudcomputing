
## How to Run the Code

Follow the steps below to run the code on your Virtual Machine.

### Prerequisites
- Virtual Machine (VM) environment set up
- SSH access to the VM

### Prerequisites
1. Update the package lists on your VM:
```shell
sudo apt-get -y update
```
2. Install Node.js and npm (Node Package Manager) on your VM:
```shell
sudo apt-get install -y nodejs npm
```
3. Install Git on your VM:
```shell
sudo apt install git
```

### Clone the Repository
1. Open the terminal on your VM.
2. Change to the directory where you want to clone the repository.
3. Clone the repository using the following command:
```shell
git clone -b Auth https://github.com/patypet-capstone/cloudcomputing.git
```
4. Change to the cloudcomputing directory:
```shell
cd cloudcomputing
```

### NPM Install
Run the following command to install the project dependencies:
```shell
npm install
```

### Configure Nginx
1. Install Nginx on your VM:
```shell
sudo apt-get install -y nginx
```
2. Open the Nginx configuration file for editing:
```shell
sudo nano /etc/nginx/sites-available/default
```
3. Replace the server settings with the following configuration:
```perl
server {
  listen 80;
  server_name YOUR_SERVERS_IP_ADDRESS;

  location / {
    proxy_pass "http://127.0.0.1:8080";
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_cache_bypass $http_upgrade;
  }
}
```
change the server_name YOUR_SERVERS_IP_ADDRESS with your external IP from VM instances

4. Save the file and exit the editor.

### Restart Nginx
To apply the changes, restart the Nginx service:
```shell
sudo service nginx restart
```

### Start the Server
1. Switch to the root user:
```shell
sudo su root
```

2. Install PM2 globally:
```shell
sudo npm install -g pm2
```

3. Start the server using PM2:
```shell
pm2 start server.js
```

### Accessing the API
The API is now ready to use. You can access it by making requests to your server's IP address on port 80.

Remember to replace YOUR_SERVERS_IP_ADDRESS with the actual IP address of your server.

For the endpoint
- POST 
    - your_ip/register
    - your_ip/login

- GET 
    - your_ip/user
    - your_ip/articles
