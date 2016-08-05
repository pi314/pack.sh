cd tmp
sh ../pack.sh test.bz2 aa bb dir1
tar jcvf test2.tar.bz2 aa bb dir1
diff test.tar.bz2 test2.tar.bz2
