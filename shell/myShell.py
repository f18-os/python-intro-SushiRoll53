import os, sys, time, re

def getFiles(command,args):
	pattern = re.compile(r'[A-Za-z]+\.[A-Za-z]+')
	matches = pattern.finditer(command)
	for match in matches:
		args.append(match[0])

def getAction(command,args):
	pattern = re.compile(r'[^A-Za-z0-9.\s]')
	matches = pattern.finditer(command)
	for match in matches:
		args.append(match[0])


running = True
while(running):
	usr_command = input("Enter command: ")
	args = []

	getFiles(usr_command,args) # gets the names of the files
	getAction(usr_command,args) # gets what is going to be done

	pid = os.getpid()

	if len(args) == 3:
		if args[2] == '|':
			pipefds = os.pipe()
			os.set_inheritable(pipefds[0], True)
			os.set_inheritable(pipefds[1], True)

		elif args[2] == '<':
				temp = args[0]
				args[0] = args[1]
				args[1] = temp

	os.write(1, ("About to fork (pid=%d)\n" % pid).encode())
	rc = os.fork() # First child

	if rc < 0:
		os.write(2, ("fork failed, returning %d\n" % rc).encode())

	elif rc == 0:
		os.write(1, ("Child: My pid==%d.  Parent's pid=%d\n" % (os.getpid(), pid)).encode())

		if args[2] == '|':
			rc = os.fork() #Second child
			print("piping")
			
			if rc == 0: # Grandchild
				os.close(0)
				os.dup(pipefds[1])
				os.close(4)
				os.close(3)
			else: # Child-Parent
				os.close(1)
				os.dup(pipefds[0])
				os.close(4)
				os.close(3)

		else:
			os.close(1)
			sys.stdout = open(args[1], "w")
			fd = sys.stdout.fileno()
			os.set_inheritable(fd, True)
			os.write(2, ("Child: opened fd=%d for writing\n" % fd).encode())


			for dir in re.split(":", os.environ['PATH']): # try each directory in path
				program = "%s/%s" % (dir, args[0])
				try:
					os.execve(program, args, os.environ) # try to exec program
				except FileNotFoundError:             # ...expected
					pass                              # ...fail quietly 

			os.write(2, ("Child:    Error: Could not exec %s\n" % args[0]).encode())
			sys.exit(1)
 

	else:
		os.write(1, ("Parent: My pid=%d.  Child's pid=%d\n" % (pid, rc)).encode())
		childPidCode = os.wait()
		os.write(1, ("Parent: Child %d terminated with exit code %d\n" % childPidCode).encode())
