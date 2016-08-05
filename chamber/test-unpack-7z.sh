cd tmp
sh ../pack.sh test.7z aa bb dir1
mv test.7z ../tmp2
cd ../tmp2
sh ../unpack.sh test.7z
rm test.7z
cd ..
diff tmp tmp2
