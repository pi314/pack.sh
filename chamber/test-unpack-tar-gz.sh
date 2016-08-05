cd tmp
sh ../pack.sh test.tar.gz aa bb dir1
mv test.tar.gz ../tmp2
cd ../tmp2
sh ../unpack.sh test.tar.gz
rm test.tar.gz
cd ..
diff tmp tmp2
