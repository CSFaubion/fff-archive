ESPN Fantasy Football league archiver. 

version 0.1.0

this project allows you to download an espn fantasy football league's history. 
you need to provide a credentials file with the following format
{
  "swid": "{12345678-ABCD-EF12-3456-789ABCDEF123}",
  "leagueId": 5
  "s2": "AREALLYLONGTOKENGOESHERE"
}
you can copy the swid and s2 cookies from your browser using dev tools after logging in.
currently this program just collects data and stuffs it into a sqlite database.
the eventual goal is to build a webservice that you can use to share your league history with your friends.
