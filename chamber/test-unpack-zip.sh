cd tmp
sh ../pack.sh test.zip aa bb dir1
mv test.zip ../tmp2
cd ../tmp2
sh ../unpack.sh test.zip
rm test.zip
cd ..
diff tmp tmp2
