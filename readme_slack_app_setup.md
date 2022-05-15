# Slack app setup
## Basic app and permissions setup
### Creating the app
* Slack > Settings & administration > Manage Apps
* In the top-right, next to the workspace downdown: Click "Build"
* "Create an App"
* "From Scratch"
* App Name: "badgeomatic".  Create App
### Enabling Socket mode
* Documentation: https://slack.dev/python-slack-sdk/socket-mode/index.html#socketmodeclient
* Slack Application Level Token 
  * Name the token `badgeomatic-alt`
  * Store in badgeomatic.cfg's `SlackTokenAL` attribute
### Adding Bot Token Scopes
* "Oauth and permissions" section from the left menu
* Add Bot Token Scopes:
  * im:history, im:read, im:write, files:read
  * Install to workspace
  * Approve scopes
  * Copy the Oauth Token
  * Store in badgeomatic.cfg's `SlackTokenOA` attribute
* "App Home" section
  * Enable Messages Tab
  * Enable Allow users to send Slash commands and messages from the messages tab
