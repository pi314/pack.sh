cd tmp
cp aa aa-orig
gzip aa
sh ../unpack.sh aa.gz
diff aa aa-orig
