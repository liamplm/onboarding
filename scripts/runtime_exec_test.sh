#!/bin/bash

set -e

BASE_PATH=$(pwd)

cd workspace/$CHALLENGE_NAME
mkdir data/  

docker container rm "$CHALLENGE_NAME-container" &> /dev/null
# sleep 0.5

echo "Running ..."
docker run --name="$CHALLENGE_NAME-container" -v /tmp/input.txt:/data/input.txt $CHALLENGE_NAME /data/input.txt > result.txt

cp $BASE_PATH/challenges/$CHALLENGE_NAME/input.txt data/input.txt
COMMAND=$(docker inspect prime --format='{{.ContainerConfig.Entrypoint}}')
CMD=${COMMAND:1:$((${#COMMAND} - 2))} #remove first and last char (long version to work on both Linux and Mac)
docker run --rm -v "$PWD/data/:/data/" --entrypoint="" $CHALLENGE_NAME  sh -c "$CMD /data/input.txt > /data/result.txt"

AVG_EXEC_TIME=0
EXEC_COUNT=5

for i in `seq 1 $EXEC_COUNT` 
do
    echo "[$i]----------------------"
    if [ $i -gt 0 ]
    then
        echo "Restarting ..."
        docker container start -a "$CHALLENGE_NAME-container" > result.txt
        sleep 1
    fi
         
    START_DATE=$(docker inspect --format='{{.State.StartedAt}}' "$CHALLENGE_NAME-container")
    STOP_DATE=$(docker inspect --format='{{.State.FinishedAt}}' "$CHALLENGE_NAME-container")

    START_TIMESTAMP=$(date --date=$START_DATE +'%s.%3N')
    STOP_TIMESTAMP=$(date --date=$STOP_DATE +'%s.%3N')

    # echo "$START_DATE ==> $START_TIMESTAMP"
    # echo "$STOP_DATE ==> $STOP_TIMESTAMP"

    EXEC_TIME=`python3 -c "print($STOP_TIMESTAMP-$START_TIMESTAMP)"`
    AVG_EXEC_TIME=`python3 -c "print($AVG_EXEC_TIME + ($EXEC_TIME / $EXEC_COUNT))"` 

    echo "$EXEC_TIME secs";
done

# echo "----------AVG------------"
# echo "$AVG_EXEC_TIME secs"
echo $AVG_EXEC_TIME

docker container rm "$CHALLENGE_NAME-container" &> /dev/null

echo 

