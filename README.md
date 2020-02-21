# MB2 ELO SYSTEM

This script is an implementation of an elo system for the popular mod Movie Battles 2. It works by reading the server log file, processing the lines, and outputting the results by socketing into said server. 

## Installing

Download or clone the files and put them in your GameData folder, and edit the mb2elo.cfg according to your needs. Make sure that no clients are already connected to the server when starting it.

### Prerequisites


```
Basic knowlege of hosting a Jedi Academy server
Python 3.7
Port 2090 forwarded through the gateway
```


## Built With

* [Visual Studio Community](https://visualstudio.microsoft.com/vs/community/)

## Authors

* **Nemanja Rajak** - [blake_won](https://github.com/blakewon)

## Acknowledgments

* [Heap Overflow](https://stackoverflow.com/users/12671057/heap-overflow) - for suggesting the most efficient way to read a file
* Inspired by those australian dudes that have their own stats thing.
