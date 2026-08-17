NAUTY ?= /tmp/nauty2_9_1
CC = gcc
CFLAGS = -O3 -march=native -mpopcnt -DMAXN=64 -I$(NAUTY)
LIBS = $(NAUTY)/nauty.a -lcrypto

.PHONY: all clean

all: bin/deckrecon bin/labelg bin/add_twofactor bin/degcheck

bin:
	mkdir -p bin

bin/deckrecon: deckrecon.c | bin
	$(CC) $(CFLAGS) -o $@ deckrecon.c $(LIBS)

bin/add_twofactor: add_twofactor.c | bin
	$(CC) $(CFLAGS) -o $@ add_twofactor.c $(NAUTY)/nauty.a

bin/degcheck: degcheck.c | bin
	$(CC) $(CFLAGS) -o $@ degcheck.c $(NAUTY)/nauty.a

bin/labelg: | bin
	cp $(NAUTY)/labelg $@
	cp $(NAUTY)/geng bin/geng
	cp $(NAUTY)/shortg bin/shortg

clean:
	rm -f bin/deckrecon
