cd tmp
sh ../pack.sh test.tar.gz aa bb dir1
tar zcvf test2.tar.gz aa bb dir1
diff test.tar.gz test2.tar.gz
