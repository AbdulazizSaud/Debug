{
sleep 0.1 
echo $2
sleep 0.1
echo $3
sleep 0.1
echo rmt list
sleep 0.1
echo exit
} | telnet 0 $1