#!/usr/bin/env python3

from colorama import init, Fore
import base64

# initialize colorama
init()

# define colors
GREEN = Fore.GREEN
RED   = Fore.RED
RESET = Fore.RESET
BLUE = Fore.BLUE

def banner():
   # if u're programmer u should be understanded bro :)
   b = "e30gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgX18Je30oYykyMDIwe30gICAgICAgICAgICAKICAgIF9fX18gIF9fX18gIF9fICBfX19fX18gX19fICAvIC9fICBfX19fX19fX18gXwogICAvIF9fIFwvIF9fIFwvIC8gLyAvIF9fIGBfXyBcLyBfXyBcLyBfX18vIF9fIGAvCiAgLyAvXy8gLyAvIC8gLyAvXy8gLyAvIC8gLyAvIC8gL18vIC8gLyAgLyAvXy8gLyAKIC8gLl9fXy9fLyAvXy9cX18sXy9fLyAvXy8gL18vXy5fX18vXy8gICBcX18sXy8gIAovXy8gICAgICAgICAgICAge30KCQlNYWtlIHdpdGgge308M3t9IGJ5IEJyeWFuIFJhbWFkaGFuCgkJVGh4IGZvciBDbG93biBIYWNrdGl2aXNtIFRlYW0=`"
   a = base64.b64decode(b).decode()
   print(a.format(GREEN, RED, GREEN, RESET, RED, RESET))
   print("\n")

def info(*text):
   print(f"{BLUE}[*]{RESET}", end=" ")
   for i in text:
      print(i)

def warn(*text):
   print(f"{RED}[!]{RESET}", end=" ")
   for i in text:
      print(i)

def ok(*text):
   print(f"{GREEN}[+]{RESET}", end=" ")
   for i in text:
      print(i)

def quest(text):
   a = input(f"{GREEN}[?]{RESET} {text} > ")
   return a