{
sleep 0.1 
echo $3
sleep 0.1
echo $4
sleep 0.1
echo service_pool name INET $2 show
sleep 0.1
echo exit
} | telnet 0 $1