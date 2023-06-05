Project Name
This is a beautiful README.md template that provides clear instructions on how to run the code.

How to Run the Code
Follow the steps below to run the code on your local machine.

Prerequisites
Virtual Machine (VM) environment set up
SSH access to the VM
Installation
Update the package lists on your VM:

shell
Copy code
sudo apt-get -y update
Install Node.js and npm (Node Package Manager) on your VM:

shell
Copy code
sudo apt-get install -y nodejs npm
Install Git on your VM:

shell
Copy code
sudo apt install git
Clone the Repository
Open the terminal on your VM.

Change to the directory where you want to clone the repository.

Clone the repository using the following command:

shell
Copy code
git clone -b dev3 https://github.com/patypet-capstone/cloudcomputing.git
Change to the cloudcomputing directory:

shell
Copy code
cd cloudcomputing
NPM Install
Run the following command to install the project dependencies:

shell
Copy code
npm install
Configure Nginx
Install Nginx on your VM:

shell
Copy code
sudo apt-get install -y nginx
Open the Nginx configuration file for editing:

shell
Copy code
sudo nano /etc/nginx/sites-available/default
Replace the server settings with the following configuration:

perl
Copy code
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
Save the file and exit the editor.

Restart Nginx
To apply the changes, restart the Nginx service:

shell
Copy code
sudo service nginx restart
Start the Server
Switch to the root user:

shell
Copy code
sudo su root
Install PM2 globally:

shell
Copy code
sudo npm install -g pm2
Start the server using PM2:

shell
Copy code
pm2 start server.js
Accessing the API
The API is now ready to use. You can access it by making requests to your server's IP address on port 80.

Remember to replace YOUR_SERVERS_IP_ADDRESS with the actual IP address of your server.

License
