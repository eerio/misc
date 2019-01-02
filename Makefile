f = hello_syscall_2
all: $(f).elf

$(f).elf: $(f).o
	gcc -o $@ $+

$(f).o: $(f).s
	as -mfpu=vfpv2 -o $@ $<

clean:
	rm -vf *.o *.out *.elf
