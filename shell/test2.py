#! /usr/bin/env python3
import sys
sum = 0
for line in sys.stdin:
	sum += int(line)
print("The total is: ",sum)