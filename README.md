## Stable Video Diffusion on Livepeer
This repository has two parts in the same api server:
- Front end: provides the html interface to request the processing
- Back end: runs the processing of stable video diffusion on the GPU
- Both can be ran on same machine or on separate machines.
  - The RUN_FRONTEND setting in start script includes the frontend endpoints in the api
  - The RUN_PROCESSING setting in the start script loads the model onto the gpu and runs the stable vidoe diffusion inference

## Installation
- setup go-livepeer using [av-livepeer-external-capabilities](https://github.com/ad-astra-video/go-livepeer/tree/av-livepeer-external-capabilities) branch of [ad-astra-video/go-livepeer](https://github.com/ad-astra-video/go-livepeer)
  - Docker image available at [adastravideo dockerhub](https://hub.docker.com/layers/adastravideo/go-livepeer/av-livepeer-external-capabilities/images/sha256-d017a7045ad68e5bd39db46cd967f5d7358561130c37581992e500a6ca9f3281?context=repo)
    - note: images will update with new builds regularly so pulling new images may break things
- setup this repo services
  - clone repository to local machine
  - run setup script (.sh if on linux, .bat if on windows)
  - run check_cuda_devices.py to get ordering of GPUS if have more than one
  - copy the example_start script and rename to use with settings specific to your machine.
    - update the GO_LIVEPEER_URL to point to orchestrator public https url
    - if running processing and front end on same machine change RUN_PROCESSING to "yes"
      - set the "backend processing setup variables"
 - #### Additional Setup
  	- go-livepeer needs real SSL cert to get requests directly to orchestrator (no self signed cert)
	  - code update is included in av-livepeer-external-capabilities that preents go-livepeer from generating a new cert.pem and key.pem at every startup
	- commands to get SSL cert from lets encrypt with DNS challenge.
              - install certbot
   
              
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
   ## TODO
   - consider moving the eth account signing to python server process
     - will allow unlocking account and signing with less prompting and is likely more secure
