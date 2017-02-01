# BAMPFA_film_calendar
A web scraper to maintain a Google calendar of BAMPFA film screenings.


## About
I made this scraper to help me keep track of the film screenings that come to the Berkeley Art Museum/Pacific Film Archive. Their calendar has the option to add individual events to your own calendar, but no option to subscribe to the entire calendar, so I decided to make my own. I've made the calendar public, so you can subscribe to it [here](https://calendar.google.com/calendar/embed?src=q8cvu1a9sn3f1l33f6s3915618%40group.calendar.google.com&ctz=America/Los_Angeles). 

The scraper currently pulls 6 months of events at a time and adds them to the calendar. I don't think BAMPFA schedules screenings much farther out than that. I then have scheduled a cron job on my person computer to execute this script once every month, presumably adding one month's worth of new events to the calendar, but also capturing any events that have been added to the months I've already captured. 

After getting this up and running without much trouble, I'm inspired to start adding more film listings from the Bay Area. If you have any suggestings for other independent cinemas that show interesting films, please leave your suggestions.

### TO DO
- Add Roxie screenings
- Add ATA screenings
