cd tmp
sh ../pack.sh test.tar.xz aa bb dir1
mv test.tar.xz ../tmp2
cd ../tmp2
sh ../unpack.sh test.tar.xz
rm test.tar
cd ..
diff tmp tmp2
