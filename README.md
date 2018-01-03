# cwstat
Crypto Wallet Status - Command line tool to manage your Crypto wallet

![alt text](https://github.com/KINOBOT/cwstat/blob/master/img/cwstat_main.png)

![alt text](https://github.com/KINOBOT/cwstat/blob/master/img/cwstat_List.png)

makes a wallet.json file in ~/.cwstat/ to keep track of your wallet. 

![alt text](https://github.com/KINOBOT/cwstat/blob/master/img/cwstat_add.png)


# requirements
python 2.7+
requests


# install
Clone the repo, run 
```basdh
sudo ./requirements 
```
to install or check for all requirements. 

Run ./cwstat to run. You can define CWSTAT_PATH to launch with an absolute path from any directory.

Alternatively add this to your ~/.bash_profile to alias the tool and set it up

```bash
export CWSTAT_PATH="/path/to/cwstat/root/dir"
alias cws="${CWSTAT_PATH}/cwstat"
```
