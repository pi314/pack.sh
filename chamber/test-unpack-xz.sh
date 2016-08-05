cd tmp
cp aa aa-orig
xz aa
sh ../unpack.sh aa.xz
diff aa aa-orig
