f () {
    sh ../pack.sh "$1" aa bb dir1 | tee "$2" > fifo
}

# echo "[$1] [$2]"
# exit

cd tmp
mkfifo fifo
f $@ &

cd ../tmp2
cat ../tmp/fifo | tee "$2" | sh ../unpack.sh "$1"

wait

cd ..
rm tmp/fifo
diff tmp tmp2
