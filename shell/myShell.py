import os, sys, time, re

running = True
while(running):
	usr_command = input("Enter command: ")
	args = usr_command.split(" ")
	for i in args:
		print(i)

	pid = os.getpid()

	os.write(1, ("About to fork (pid=%d)\n" % pid).encode())
	rc = os.fork()

	if rc < 0:
		os.write(2, ("fork failed, returning %d\n" % rc).encode())

	elif rc == 0:
		os.write(1, ("##CHILD ID=%d.  Parent's pid=%d\n" % (os.getpid(), pid)).encode())

		if len(args) >= 3:
			if args[2] == '<':
				temp = args[len(args)-3]
				args[len(args)-3] = args[len(args)-1]
				args[len(args)-1] = temp
				args.remove("<")
			try:
				args.remove(">")
			except ValueError:
				pass
			os.close(1)
			sys.stdout = open(args[len(args)-1], "w")
			fd = sys.stdout.fileno()
			os.set_inheritable(fd, True)
			os.write(2, ("##Child: opened fd=%d for writing\n" % fd).encode())

		argsC = [args[0],args[1]]
		for dir in re.split(":", os.environ['PATH']): # try each directory in path
			program = "%s/%s" % (dir, args[0])
			try:
				os.execve(program, argsC, os.environ) # try to exec program
			except FileNotFoundError:             # ...expected
				pass                              # ...fail quietly 

		os.write(2, ("##Child:    Error: Could not exec %s\n" % args[0]).encode())
		sys.exit(1)
 

	else:
		os.write(1, ("Parent: My pid=%d.  Child's pid=%d\n" % (pid, rc)).encode())
		childPidCode = os.wait()
		os.write(1, ("Parent: Child %d terminated with exit code %d\n" % childPidCode).encode())