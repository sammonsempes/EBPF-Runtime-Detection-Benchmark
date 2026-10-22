CC ?= gcc
CFLAGS ?= -O2 -Wall -Wextra -std=c11
BINDIR ?= bin
WORKLOADS := syscall exec fileio

.PHONY: all clean

all: $(addprefix $(BINDIR)/,$(WORKLOADS))

$(BINDIR)/%: %.c common.h
	mkdir -p $(BINDIR)
	$(CC) $(CFLAGS) -o $@ $<

clean:
	rm -rf $(BINDIR)
