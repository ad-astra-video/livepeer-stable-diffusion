- clone repository to local machine
- run setup script (.sh if on linux, .bat if on windows)
- run check_cuda_devices.py to get ordering of GPUS if have more than one
- copy the example_start script and rename to use with settings specific to your machine.
- Additional Setup:
	- go-livepeer needs real SSL cert to get requests directly to orchestrator (no self signed cert)
	- this needed go-livepeer code update to not generate cert/key with every startup
	- commands
	      //install certbot
	      sudo apt-get install certbot
	      sudo certbot certonly --manual --preferred-challenges dns -d "*.{DOMAIN}"
	      //now set the TXT record on dns and verify with https://mxtoolbox.com/txtlookup.aspx
	      //create symlink to go-livepeer install path for certs created
	      cd [path to go-livepeer datadir]
	      rm cert.pem key.pem
	      cp [path to letsencrypt cert] ./cert.pem
	      cp [path to letsencrypt key] ./key.pem
	      chown [user]:[user] cert.pem
	      chown [user]:[user] key.pem