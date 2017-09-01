# Yahoo! Fantasy Hockey Line Setter 2017-18

## Introduction
This app is a _very_ hacky app that will automatically set lines for your Yahoo! Fantasy Hockey team, with a few caveats.  This uses oAuth to authenticate with your team and then uses the Fantasy Sports API to set the lines.

## Caveats (IMPORTANT)

Because this app only really needs to be used once at the very beginning of the season, there are a bunch of things to remember when using this app:

* Lineup conflicts *WILL* occur with players of multiple position types if one of the positions is at capacity.  Logic might be added later, but I don't really care.
* This only works with the default lineup settings of 2 starting Centers, LW, RW, G and 4 Defencemen.  All other positions will be benched
* Because of the way the rosters are set, all non active players will be _benched_
* This will break if there is a change in the schedule

Feel free to checkout a live version of this at http://nhllines2017.pythonanywhere.com