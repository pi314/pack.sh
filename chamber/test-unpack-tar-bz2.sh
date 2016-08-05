cd tmp
sh ../pack.sh test.tar.bz2 aa bb dir1
mv test.tar.bz2 ../tmp2
cd ../tmp2
sh ../unpack.sh test.tar.bz2
rm test.tar.bz2
cd ..
diff tmp tmp2
