:<<"::CMDLITERAL"
@ECHO OFF
GOTO :CMDSCRIPT
::CMDLITERAL

# Allows execution from Windows with bash. Windows Code at the end.
if :; then


URL='https://XXXXX--pse.na156.visual.force.com'


INPUT=''

if [ "" == "`which jq`" ]; then echo "jq not found"; if [ -n "`which apt-get`" ]; then sudo apt-get -y install jq ; elif [ -n "`which yum`" ]; then sudo yum -y install jq ; fi ; fi
if [ "" == "`which curl`" ]; then echo "jq not found"; if [ -n "`which apt-get`" ]; then sudo apt-get -y install curl ; elif [ -n "`which yum`" ]; then sudo yum -y install curl ; fi ; fi


echo "Paste SID/Cookie/Curl/Header etc and confirm completion by pressing CTRL+D"
echo "Option + ⌘ + J (on Safari), or Shift + CTRL + E (on Firefox)."
while true; do
    line=''

    while IFS= read -r -N 1 ch; do
        case "$ch" in
            $'\04') got_eot=1   ;&
            $'\n')  break       ;;
            *)      line="$line$ch" ;;
        esac
    done

    INPUT="$INPUT $line"

    if (( got_eot )); then
        break
    fi
done
#echo $INPUT
echo ""
SID=$( printf "%s\n" "${INPUT#*sid}" )
SID=$( cut -d ";" -f1 <<< $SID| cut -d "," -f1 | sed s/\"//g | cut -c 2- )
echo ""
echo "Fetching Salesforce data..."


INFILE='TAMTT_VARIABLE_TIMESHEET_JSON'
STARTDATE=`echo $INFILE | jq -r '.[0]'`
STARTDATESTUPID=`echo $INFILE | jq -r '.[4]'`
ENDDATE=`echo $INFILE | jq -r '.[2]'`
ENDDATEUS=`echo $INFILE | jq -r '.[3]'`
ENDDATESTUPID=`echo $INFILE | jq -r '.[5]'`


DRLIST=`echo $INFILE | jq -c '.[1] |keys' | grep -o '\bDR[0-9]\{7\}\b' | xargs`


mkdir -p tmp
rm -Rf tmp/*


curl ${URL}'/apex/PSATimecardEntry?retURL=%2FaEL%2Fo&save_new=1&sfdc.override=1' \
	  --silent \
          --compressed \
          --globoff \
          -H "Referer: ${URL}" \
          -H 'Connection: keep-alive' \
          -H "Cookie: sid=${SID}" \
          -H 'Pragma: no-cache' \
          -H 'Cache-Control: no-cache' > tmp/PSATimecardEntry.html 


TAMTT_VARIABLE_RESOURCEID=`cat tmp/PSATimecardEntry.html | grep currentResourceId | sed -n "s/^.*'\(.*\)'.*$/\1/ p"`
# Fix vim '"

# GET DATA

## Create timesheet...
ACTION="pse.SenchaProjAssignmentSelector"
METHOD="getRecentProjectAssignemnts"
CSRF=`grep VFRM.RemotingProviderImpl tmp/PSATimecardEntry.html | sed 's/.*VFRM.RemotingProviderImpl(//' | sed 's/));$//' | jq -r '.actions."'$ACTION'".ms[] | select(.name == "'$METHOD'") | .csrf'`

curl ${URL}/apexremote \
	--silent \
        --compressed \
        -H "Referer: ${URL}/apex/PSATimecardEntry?retURL=%2FaEL%2Fo&save_new=1&sfdc.override=1" \
        -H 'X-User-Agent: Visualforce-Remoting' \
        -H 'Content-Type: application/json' \
        -H 'X-Requested-With: XMLHttpRequest' \
        -H "Origin: ${URL}" \
        -H 'Connection: keep-alive' \
        -H "Cookie: sid=${SID}" \
        -H 'Pragma: no-cache' \
        -H 'Cache-Control: no-cache'  \
        --data-raw '{"action":"pse.SenchaProjAssignmentSelector","method":"getRecentProjectAssignemnts","data":[{"resourceId":"'${TAMTT_VARIABLE_RESOURCEID}'","weekEndDate":"'${ENDDATEUS}'","searchStr":""}],"type":"rpc","tid":11,"ctx":{"csrf":"'${CSRF}'","vid":"06614000001UYes","ns":"pse","ver":41}}' > tmp/getrecentprojectassignments

### LOOP HERE
for DR in $DRLIST
do
	ASSIGNMENT=`cat tmp/getrecentprojectassignments | jq -c '.[0].result.assignments[]| select(.Project__r.Name | contains("'$DR'")) | {Id, Project__c, Account__c: .Project__r.Account__c  }'`
	mkdir -p tmp/$DR


### Create datatimecardhead
	TAMTT_VARIABLE_PROJECTID=`jq -r .Project__c <<< $ASSIGNMENT`
	TAMTT_VARIABLE_ACCOUNTID=`jq -r .Account__c <<< $ASSIGNMENT`
	TAMTT_VARIABLE_ASSIGNMENTID=`jq -r .Id <<< $ASSIGNMENT`

### Create datatimecardfooter
### Deliverables in taskTimeDetails

#### Get task lists
        ACTION="pse.ProjectTaskSelector"
	METHOD="getTaskHierarchySenchaTC"
	CSRF=`grep VFRM.RemotingProviderImpl tmp/PSATimecardEntry.html | sed 's/.*VFRM.RemotingProviderImpl(//' | sed 's/));$//' | jq -r '.actions."'$ACTION'".ms[] | select(.name == "'$METHOD'") | .csrf'`
	echo '{"action":"'$ACTION'","method":"'$METHOD'","data":[{"projectId":"'${TAMTT_VARIABLE_PROJECTID}'","resourceId":"'${TAMTT_VARIABLE_RESOURCEID}'","startDate":"'${STARTDATESTUPID}'","endDate":"'${ENDDATESTUPID}'","assignmentId":"'${TAMTT_VARIABLE_ASSIGNMENTID}'"}],"type":"rpc","tid":12,"ctx":{"csrf":"'${CSRF}'","vid":"06614000001UYes","ns":"pse","ver":41}}' > tmp/${DR}/tmptasks
	curl ${URL}/apexremote \
	  --silent \
          --compressed \
	  --globoff \
          -H "Referer: ${URL}apex/PSATimecardEntry?retURL=%2FaEL%2Fo&save_new=1&sfdc.override=1" \
          -H 'X-User-Agent: Visualforce-Remoting' \
          -H 'Content-Type: application/json' \
          -H 'X-Requested-With: XMLHttpRequest' \
          -H "Origin: ${URL}" \
          -H 'Connection: keep-alive' \
          -H "Cookie: sid=${SID}" \
          -H 'Pragma: no-cache' \
          -H 'Cache-Control: no-cache'  \
	  -d @tmp/${DR}/tmptasks > tmp/${DR}/tasks


#### Get milestone
        ACTION="pse.SenchaTCController"
        METHOD="getAssignmentDetails"
        CSRF=`grep VFRM.RemotingProviderImpl tmp/PSATimecardEntry.html | sed 's/.*VFRM.RemotingProviderImpl(//' | sed 's/));$//' | jq -r '.actions."'$ACTION'".ms[] | select(.name == "'$METHOD'") | .csrf'`
	curl ${URL}/apexremote \
	  --silent \
          --compressed \
          -H "Referer: ${URL}/apex/PSATimecardEntry?retURL=%2FaEL%2Fo&save_new=1&sfdc.override=1" \
          -H 'X-User-Agent: Visualforce-Remoting' \
          -H 'Content-Type: application/json' \
          -H 'X-Requested-With: XMLHttpRequest' \
          -H "Origin: ${URL}" \
          -H 'Connection: keep-alive' \
          -H "Cookie: sid=${SID}" \
          -H 'Pragma: no-cache' \
          -H 'Cache-Control: no-cache'  \
          --data-raw '{"action":"pse.SenchaTCController","method":"getAssignmentDetails","data":["'${TAMTT_VARIABLE_ASSIGNMENTID}'","'${ENDDATEUS}'","'${RESOURCEID}'"],"type":"rpc","tid":27,"ctx":{"csrf":"'${CSRF}'","vid":"06614000001UYes","ns":"pse","ver":41}}' > tmp/${DR}/milestoneid

	TAMTT_VARIABLE_MILESTONEID=$(cat tmp/${DR}/milestoneid | jq -r '.[].result' | sed s/\\\\//g | jq -r '[.[].milestones[]] | max_by(.name).id')
	SUMSAT=`echo $INFILE | jq -r '.[6] | to_entries[] | select(.key|contains("'"$DR"'") )  | .value[5]'`
	SUMSUN=`echo $INFILE | jq -r '.[6] | to_entries[] | select(.key|contains("'"$DR"'") )  | .value[6]'`
	SUMMON=`echo $INFILE | jq -r '.[6] | to_entries[] | select(.key|contains("'"$DR"'") )  | .value[0]'`
	SUMTUE=`echo $INFILE | jq -r '.[6] | to_entries[] | select(.key|contains("'"$DR"'") )  | .value[1]'`
	SUMWED=`echo $INFILE | jq -r '.[6] | to_entries[] | select(.key|contains("'"$DR"'") )  | .value[2]'`
	SUMTHU=`echo $INFILE | jq -r '.[6] | to_entries[] | select(.key|contains("'"$DR"'") )  | .value[3]'`
	SUMFRI=`echo $INFILE | jq -r '.[6] | to_entries[] | select(.key|contains("'"$DR"'") )  | .value[4]'`


	TIMECARDHEAD='\"timecard\":{\"Assignment__c\":\"TAMTT_VARIABLE_ASSIGNMENTID\",\"Resource__c\":\"TAMTT_VARIABLE_RESOURCEID\",\"Project__c\":\"TAMTT_VARIABLE_PROJECTID\",\"Start_Date__c\":\"TAMTT_VARIABLE_STARTDATE\",\"End_Date__c\":\"TAMTT_VARIABLE_ENDDATE\",\"Billable__c\":false,
\"Project__r\":{\"attributes\":{\"type\":\"pse__Proj__c\",\"url\":\"/services/data/v51.0/sobjects/pse__Proj__c/TAMTT_VARIABLE_PROJECTID\"},\"Account__c\":\"TAMTT_VARIABLE_ACCOUNTID\",\"Id\":\"TAMTT_VARIABLE_PROJECTID\",\"Account__r\":{\"attributes\":{\"type\":\"Account\",\"url\":\"/services/data/v51.0/sobjects/Account/TAMTT_VARIABLE_ACCOUNTID\"},\"Id\":\"TAMTT_VARIABLE_ACCOUNTID\",\"RecordTypeId\":\"0123000000007NBAAY\"}},
\"Saturday_Hours__c\":'$SUMSAT',\"Saturday_Notes__c\":\"Automatic submission by TAMTT\",
\"Sunday_Hours__c\":'$SUMSUN',\"Sunday_Notes__c\":\"Automatic submission by TAMTT\",
\"Monday_Hours__c\":'$SUMMON',\"Monday_Notes__c\":\"Automatic submission by TAMTT\",
\"Tuesday_Hours__c\":'$SUMTUE',\"Tuesday_Notes__c\":\"Automatic submission by TAMTT\",
\"Wednesday_Hours__c\":'$SUMWED',\"Wednesday_Notes__c\":\"Automatic submission by TAMTT\",
\"Thursday_Hours__c\":'$SUMTHU',\"Thursday_Notes__c\":\"Automatic submission by TAMTT\",
\"Friday_Hours__c\":'$SUMFRI',\"Friday_Notes__c\":\"Automatic submission by TAMTT\",
\"Assignment__r\":{\"attributes\":{\"type\":\"pse__Assignment__c\",\"url\":\"/services/data/v51.0/sobjects/pse__Assignment__c/TAMTT_VARIABLE_ASSIGNMENTID\"},\"Id\":\"TAMTT_VARIABLE_ASSIGNMENTID\"},
\"Milestone__c\":\"TAMTT_VARIABLE_MILESTONEID\"},\"taskTimeDetails\":{\"taskTimes\":['

        echo $TIMECARDHEAD | sed s/TAMTT_VARIABLE_STARTDATE/${STARTDATE}/g > tmp/${DR}/datatimecardhead
        sed -i s/TAMTT_VARIABLE_ENDDATE/${ENDDATE}/g tmp/${DR}/datatimecardhead
        sed -i s/TAMTT_VARIABLE_PROJECTID/${TAMTT_VARIABLE_PROJECTID}/g tmp/${DR}/datatimecardhead
        sed -i s/TAMTT_VARIABLE_ACCOUNTID/${TAMTT_VARIABLE_ACCOUNTID}/g tmp/${DR}/datatimecardhead
        sed -i s/TAMTT_VARIABLE_ASSIGNMENTID/${TAMTT_VARIABLE_ASSIGNMENTID}/g tmp/${DR}/datatimecardhead
        sed -i s/TAMTT_VARIABLE_RESOURCEID/${TAMTT_VARIABLE_RESOURCEID}/g tmp/${DR}/datatimecardhead
	sed -i s/TAMTT_VARIABLE_MILESTONEID/${TAMTT_VARIABLE_MILESTONEID}/g tmp/${DR}/datatimecardhead


##### Timecard Tasks

### CREATE TIMECARDTASKDATA HERE

	DELIVERABLES=`echo $INFILE | jq '.[1] | to_entries[] | select(.key|contains("'"$DR"'") ) | .value | keys | .[]'`
	while IFS= read -r line;
	do

		TASK=`sed "s/[^[:alpha:]]//g" <<< $line`;
		[ -z "$TASK" ] && continue;
		TASKID=`cat tmp/${DR}/tasks | jq -r '.[].result.data[] | select(.Name|gsub("[^[:alpha:]]";"")|test("'"$TASK"'")) | .Id'`;
		[ -z "$TASKID" ] && continue;
                SAT=`echo $INFILE | jq -r '.[1] | to_entries[] | select(.key|contains("'"$DR"'") ) | .value."'"$( echo $line | xargs)"'"[5]'`
		SUN=`echo $INFILE | jq -r '.[1] | to_entries[] | select(.key|contains("'"$DR"'") ) | .value."'"$( echo $line | xargs)"'"[6]'`
		MON=`echo $INFILE | jq -r '.[1] | to_entries[] | select(.key|contains("'"$DR"'") ) | .value."'"$( echo $line | xargs)"'"[0]'`
		TUE=`echo $INFILE | jq -r '.[1] | to_entries[] | select(.key|contains("'"$DR"'") ) | .value."'"$( echo $line | xargs)"'"[1]'`
		WED=`echo $INFILE | jq -r '.[1] | to_entries[] | select(.key|contains("'"$DR"'") ) | .value."'"$( echo $line | xargs)"'"[2]'`
		THU=`echo $INFILE | jq -r '.[1] | to_entries[] | select(.key|contains("'"$DR"'") ) | .value."'"$( echo $line | xargs)"'"[3]'`
		FRI=`echo $INFILE | jq -r '.[1] | to_entries[] | select(.key|contains("'"$DR"'") ) | .value."'"$( echo $line | xargs)"'"[4]'`

                if test -f "tmp/${DR}/timecardtaskwip"; then
                    echo "," >> tmp/${DR}/timecardtaskwip
                 else
	            touch tmp/${DR}/timecardtaskwip
                fi

		TASKDATA='{"taskTime":{"Project_Task__c":"aDo1O000000k9rtSAA","Saturday_Hours__c":7,"Sunday_Hours__c":0,"Monday_Hours__c":1,"Tuesday_Hours__c":0,"Wednesday_Hours__c":0,"Thursday_Hours__c":4,"Friday_Hours__c":0},"id":"PSATaskTime_1000","internalTimecardId":"PSATimecard_1000","startDate":"2021-05-15","dirty":true,"projectTask":{"Id":"aDo1O000000k9rtSAA"}}'

		echo $TASKDATA | jq '. | .startDate="'$STARTDATE'" | .projectTask.Id="'$TASKID'" | .taskTime.Saturday_Hours__c='$SAT' | .taskTime.Sunday_Hours__c='$SUN' | .taskTime.Monday_Hours__c='$MON' | .taskTime.Tuesday_Hours__c='$TUE' | .taskTime.Wednesday_Hours__c='$WED' | .taskTime.Thursday_Hours__c='$THU' | .taskTime.Friday_Hours__c='$FRI' |  .taskTime.Project_Task__c=.projectTask.Id | .taskTime.Start_Date__c=.startDate' >> tmp/${DR}/timecardtaskwip
	done <<< $DELIVERABLES

	echo ']}' >> tmp/${DR}/timecardtaskwip
        sed -i s/\"/\\\\\"/g tmp/${DR}/timecardtaskwip

        if test -f "tmp/datawip"; then
          echo ',{ \"id\":\"PSATimecard_1000\",' >> tmp/datawip
	else
	  echo '{ \"id\":\"PSATimecard_1000\",' > tmp/datawip
        fi

	cat tmp/${DR}/datatimecardhead tmp/${DR}/timecardtaskwip >> tmp/datawip
	echo "}" >> tmp/datawip

done

echo "]\",\"${ENDDATEUS}\",\"${TAMTT_VARIABLE_RESOURCEID}\",[],[]]" >> tmp/datawip


ACTION="pse.SenchaTCController"
METHOD="saveTimecard"
CSRF=`grep VFRM.RemotingProviderImpl tmp/PSATimecardEntry.html | sed 's/.*VFRM.RemotingProviderImpl(//' | sed 's/));$//' | jq -r '.actions."'$ACTION'".ms[] | select(.name == "'$METHOD'") | .csrf'`

# Create ctx file (DONE)
#	sed s/TAMTT_VARIABLE_CSRF/${CSRF}/ body > tmp/body

echo '"ctx":{"csrf":"'${CSRF}'","vid":"06614000001UYes","ns":"pse","ver":41},
"action":"pse.SenchaTCController","method":"saveTimecard","type":"rpc","tid":12,
"data":["[' > tmp/body



# Create final timecard json for sumission (DONE)
(echo "{"
cat tmp/body tmp/datawip
echo "}") > tmp/timecard.json

curl ${URL}/apexremote \
	--silent \
	--compressed \
	-H "Referer: ${URL}/apex/PSATimecardEntry?retURL=%2FaEL%2Fo&save_new=1&sfdc.override=1" \
	-H 'X-User-Agent: Visualforce-Remoting' \
	-H 'Content-Type: application/json' \
	-H 'X-Requested-With: XMLHttpRequest' \
	-H "Origin: ${URL}" \
	-H 'Connection: keep-alive' \
	-H "Cookie: sid=${SID}" \
	-H 'Pragma: no-cache' \
	-H 'Cache-Control: no-cache'  \
	-d @tmp/timecard.json > tmp/uploadreply

head -c 100 tmp/uploadreply
cp $0 tmp
echo ""
echo "Tranfer completed. Verify status 200 above."

# Windows Code below to start this script as bash
fi
exit $?


:CMDSCRIPT
bash %~nx0
exit /b
