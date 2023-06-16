
## How to Run the Code

Follow the steps below to run the code on your local machine.

### Prerequisites
- Virtual Machines
- SSH access to the VM
- Machine Learning Model
- Service Account Key

### Virtual machines

1. Create a virtual machine (VM) in the us-central1 region, using the n1-standard1 machine type, allowing HTTP and HTTPS traffic, reserving a static external IP, and create it.

2. Once it's finished, run SSH.

3. Update the package list on the VM:
```shell
sudo apt update
sudo apt upgrade
```

4. Install Git on the VM:
```shell
sudo apt install git
```

### Clone the Repository
1. Clone the code from GitHub:
```shell
git clone -b flask https://github.com/patypet-capstone/cloudcomputing.git
```
2. Change to the cloudcomputing directory:
```
cd cloudcomputing
```

### Setup Python Environment
1. Install Python by running the following command:
```shell
sudo apt install python3-pip
```
2. Create a virtual environment for your Flask project by executing the following command:
```shell
sudo apt install python3.10-venv
python3 -m venv myenv
```
3. Activate the virtual environment by running the following command:
```shell
source myenv/bin/activate
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
change the server_name YOUR_SERVERS_IP_ADDRESS with your external IP from intances

4. Save the file and exit the editor.

### Restart Nginx
To apply the changes, restart the Nginx service:
```shell
sudo service nginx restart
```

### Configure Flask
1. Install the required dependencies:
```shell
pip install -r requirements.txt
```
2. Create a service account to obtain the key.json file.
3. Upload the key.json file via SSH.
4. Move the key.json file to the Flask directory.

5. Download the machine learning model from Google Drive:
```shell
wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1eCN2VvRJ275anll37eMP0gc5eGe6dRZg' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1eCN2VvRJ275anll37eMP0gc5eGe6dRZg" -O model.hdf5 && rm -rf /tmp/cookies.txt
```

6. Run the Flask app using the following command:
```shell
python3 main.py
```

### Accessing the API
The API is now ready to use. You can access it by making requests to your server's IP address on port 8080.

Remember to replace "YOUR_SERVERS_IP_ADDRESS" with the actual IP address of your server.

For the endpoint:
- POST: your_ip/upload
- POST: your_ip/save
- PUT : your_ip/pet/edit?id={id}&name={name}
- GET : your_api/pet/edit?id={id}&name={name}
- GET : your_api/pet/{email}
- GET : your_api/pet/{email}/{id}

### Contributing
Contributions are welcome! If you find any issues or have suggestions for improvements, feel free to open an issue or create a pull request.
