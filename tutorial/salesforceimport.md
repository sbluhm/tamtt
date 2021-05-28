# Salesforce import script.

The salesforce script is a bash script that contains all relevant code to push a timesheet json to Salesforce.

## Preparing your data

The project/assignment is matched by a "DR" number which consists of the characters DR and 7 digits. So both, the Salesforce assignment and the Outlook category must contain that pattern. You can modify it in the bash script if required.

Tasks are matched by the character sequence. All non-alphabetical characters are stripped. The rest is then tested to be contained within Salesforce tasks (so subsections. Not complete matches).

## Running the script

When you run the bash script, it will ask you to input an SID. To get an SID, log into Salesforce, open the developer mode in your browser (<F12> on Chrome and Firefox).
Monitor the Network analysis screen and trigger a salesforce request. Select any of the requests and the header or cookie for the SID value. You can also right click on the request and copy the the request as curl.

Paste the data into the bash script window and confirm the completed by pressing CTRL + D. You can pretty much paste anything in there as long as it contains the tag "sid" which is terminated by a ";" or "}".

Now the request will be sent to Salesforce. After a while the script completes and returns the first few characters oft the salesforce response. It should include a status code 200 in the text.

Each script run creates a tmp folder with the calculated/loaded/used run time values. Zip and send the tmp folder for debugging.

## Configuring the script

Just update the URL to point to the right server.
Maybe you want to adapt the script above for the detection logic to suit your needs.
