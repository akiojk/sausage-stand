# How many Sausages
This tells you the exact number of sausages at certain sausage stands. 

## Installation
This script runs with Python 3 and requires the following modules installed:

```bash
pip3 install requests
```
```bash
pip3 install selenium
```
```bash
pip3 install webdriver-manager
```

## Usage
```bash
python3 sausage.py <url> [instock only: yes]
```

## Example

To see the sausage stock level of all sausage stands:
```bash
python3 sausage.py https://thesausagewebsite.com/sausageurl
```

To see a list of sausage stands actually have that sausage in stock:
```
python3 sausage.py https://thesausagewebsite.com/sausageurl yes
```
## Q&A
> Q: When I run the script I see error "Please obtain clientId from the sausage website and insert at line 16 of this script"
>
> A: You'll need `clientId` from the sausage website.