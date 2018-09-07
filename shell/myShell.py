import os, sys, time, re, stat

def getFiles(command,args):
	pattern = re.compile(r'[A-Za-z]+\.[A-Za-z]+')
	matches = pattern.finditer(command)
	for match in matches:
		print(match[0])
		args.append(match[0])

def getAction(command,args):
	pattern = re.compile(r'[^A-Za-z0-9.\s]')
	matches = pattern.finditer(command)
	for match in matches:
		print(match[0])
		args.append(match[0])


running = True
while(running):
	usr_command = input("Enter command: ")
	args = []

	getFiles(usr_command,args)
	getAction(usr_command,args)

	print(args)

	pid = os.getpid()

	os.write(1, ("About to fork (pid=%d)\n" % pid).encode())
	rc = os.fork()

	if rc < 0:
		os.write(2, ("fork failed, returning %d\n" % rc).encode())

	elif rc == 0:
		os.write(1, ("Child: My pid==%d.  Parent's pid=%d\n" % (os.getpid(), pid)).encode())

		if len(args) == 3:
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
