CC = gcc
CFLAGS = -O3 -std=c11 -Wall -Wextra

sieve_n2p1: sieve_n2p1.c
	$(CC) $(CFLAGS) sieve_n2p1.c -o sieve_n2p1

.PHONY: clean test
clean:
	rm -f sieve_n2p1

test: sieve_n2p1
	./sieve_n2p1 --self-test
