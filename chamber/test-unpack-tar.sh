cd tmp
sh ../pack.sh test.tar aa bb dir1
mv test.tar ../tmp2
cd ../tmp2
sh ../unpack.sh test.tar
rm test.tar
cd ..
diff tmp tmp2
