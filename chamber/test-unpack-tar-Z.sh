cd tmp
sh ../pack.sh test.tar.Z aa bb dir1
mv test.tar.Z ../tmp2
cd ../tmp2
sh ../unpack.sh test.tar.Z
rm test.tar
cd ..
diff tmp tmp2
