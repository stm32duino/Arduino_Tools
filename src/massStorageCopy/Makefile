all: massStorageCopy32 massStorageCopy


massStorageCopy32: massStorageCopy32.o
	gcc -m32 -o $@ $<

massStorageCopy32.o: massStorageCopy.c
	gcc -m32 -c $<
	mv massStorageCopy.o massStorageCopy32.o
     
massStorageCopy: massStorageCopy.o
	gcc -o $@ $<

massStorageCopy.o: massStorageCopy.c
	gcc -c $<

clean:
	rm -f *.o massStorageCopy massStorageCopy32

install:
	mv massStorageCopy ../../linux64/
	mv massStorageCopy32 ../../linux/massStorageCopy
