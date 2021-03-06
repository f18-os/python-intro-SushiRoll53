#! /usr/bin/env python3
import os, sys, time, re
os.environ["PS1"] = "$ "
# The prompt will only close if the user types exit
while(True):
	# Checks what the user type, and gives priority to PS1 and Exit
	usr_command = input(os.environ["PS1"])
	check = usr_command.split("=")
	if check[0] == "export PS1 " or check[0] == "export PS1":
		os.environ["PS1"] = check[1].replace("\"","").replace(" ","")
		continue
	if usr_command.lower() == "exit":
		break
	args = usr_command.split(" ")
	piping = False
	# Checks if the user entered 3 or more arguments
	if len(args) >= 3:
		# If it has a pipe, we connect the pipe
		if args[1] == '|':
			r, w = os.pipe() # Start the pipe
			os.set_inheritable(r, True) # To Read
			os.set_inheritable(w, True) # To Write
			piping = True

	pid = os.getpid() #Parent's ID

	os.write(1, ("About to fork (pid=%d)\n" % pid).encode())
	rc = os.fork()
	# First child
	if rc == 0:
		os.write(1, ("##CHILD ID=%d.  Parent's pid=%d\n" % (os.getpid(), pid)).encode())

		if len(args) < 3:
			for dir in re.split(":", os.environ['PATH']+":."): # try each directory in path
				program = "%s/%s" % (dir, args[0])
				try:
					os.execve(program, args, os.environ) # try to exec program
				except FileNotFoundError:             # ...expected
					pass                              # ...fail quietly 

			os.write(2, ("##Child:    Error: Could not exec %s\n" % args[0]).encode())

		elif len(args) >= 3 and args[1] != '|':
			if args[1] == '<':
				temp = args[len(args)-3]
				args[len(args)-3] = args[len(args)-1]
				args[len(args)-1] = temp
			args.pop(1)

			os.close(1)
			sys.stdout = open(args[len(args)-1], "w")
			fd = sys.stdout.fileno()
			os.set_inheritable(fd, True)
			os.write(2, ("##Child: opened fd=%d for writing\n" % fd).encode())

			argsC = [args[0],args[1]]
			for dir in re.split(":", os.environ['PATH']+":."): # try each directory in path
				program = "%s/%s" % (dir, args[0])
				try:
					os.execve(program, argsC, os.environ) # try to exec program
				except FileNotFoundError:             # ...expected
					pass                              # ...fail quietly 

			os.write(2, ("##Child:    Error: Could not exec %s\n" % args[0]).encode())

		else:
			args.pop(1)
			os.write(1, ("About to fork (pid=%d)\n" % os.getpid()).encode())
			rc1 = os.fork() # Creates a Grandchild
			if rc1 == 0:
				print("####GRANDCHILD - will write into the pipe")
				os.close(1)
				os.dup(w)
				os.set_inheritable(1, True) 
				for i in (r, w):
					os.close(i)
				sys.stdout = os.fdopen(1,'w') 

				for dir in re.split(":", os.environ['PATH']+":."): # try each directory in path
					program = "%s/%s" % (dir, args[0])
					try:
						os.execve(program, args, os.environ) # try to exec program
					except FileNotFoundError:             # ...expected
						pass                              # ...fail quietly 

				os.write(2, ("##Child:    Error: Could not exec %s\n" % args[0]).encode())

			else:
				print("####CHILD - will read from the pipe")
				os.close(w)
				os.wait()
				os.write(1, ("##CHILD AND PARENT ID=%d.  Parent's pid=%d\n" % (os.getpid(), pid)).encode())
				os.close(0)
				os.dup(r)
				os.set_inheritable(0, True) 
				os.close(r)
				sys.stdin = os.fdopen(0,'r')

				for dir in re.split(":", os.environ['PATH']+":."): # try each directory in path
					program = "%s/%s" % (dir, args[1])
					try:
						os.execve(program, args, os.environ) # try to exec program
					except FileNotFoundError:             # ...expected
						pass                              # ...fail quietly 

				os.write(2, ("##Child:    Error: Could not exec %s\n" % args[1]).encode())
	else:
		# If a pipe was entered by the user, we close the aditional output (w)
		if piping:
			os.close(w)
		os.write(1, ("Parent: My pid=%d.  Child's pid=%d\n" % (pid, rc)).encode())
		childPidCode = os.wait()
		os.write(1, ("Parent: Child %d terminated with exit code %d\n" % childPidCode).encode())
