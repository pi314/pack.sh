cd tmp
cp aa aa-orig
bzip2 aa
sh ../unpack.sh aa.bz2
diff aa aa-orig
