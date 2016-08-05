cd tmp
cp aa aa-orig
compress aa
sh ../unpack.sh aa.Z
diff aa aa-orig
