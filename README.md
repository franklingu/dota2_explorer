Dota2 explorer
=============================================================

Explore stats of Dota2!

### Installation

* Production: Requires docker and docker-compose installed
  - modify deployment files, especially 'deployment/environ/deployment.env' and 'deployment/nginx/ssl' 
  - `docker-compose up`
* Development: Requires Python 3.5+, pip and sqlite3 extension installed
  - create virtual env under 'backend' if needed and activate it, navigate to 'backend'
  - `pip install -r requirements.txt`
  - `python manage.py makemigrations`
  - `python manage.py runserver_plus` : runserver_plus provides some more awesomeness to the development server

### Architechture

* backend: PostgreSQL in production and SQLite in development.
  - SQLite is very light-weight and easy to configure for development. For development, the load is also light enough for it to handle. There is no need to take care of authentication and other complications.
  - PostgreSQL is chosen mainly because I am familiar with it. Compared to MySQL, it is slightly better for analytics purpose because its engine's design. As for NoSQL databases, MongoDB could be a great fit in this case as its support for JSON and analytics are better compared to SQL -- However, use of MongoDB or other NoSQL databases will bring a lot of headache due to the fact that the backend framework is Django, which is far more friendly for SQL.
  - Django is choson over Flask or newer frameworks (mostly async) like Sanic or Vibora. Sanic's and Vibora's support for async should be able to greatly improve performance as this application requires requests to remote apis and analytics -- which normally takes quite some time. Async should be able to improve concurrency in this case. However, these frameworks are quite new and supports may not be enough. What is more, async itself may bring more headache into programming. And one more important factor is that I am not familiar with them. Flask is more light-weight compared to Django and its community is great as well. For such a small application Flask seems to be a better fit as well -- which will bring simpler design and more control. The only Django wins this race is the time: with Django command line, getting started/setup is easy enough.
* frontend: I do not have time to implement this part, although if I had time I would have gone for Vue.js, with which I have a bit of experience.
* testing: due to time limit, I did not implement any automatic testing.

### Future Work

* compare_players api is quite dummy for now. Part of the reason is because of time limit and part of the reason is also that I do not play this game and I do not have a clear vision of this.
* recommend_hero currently does not take weight into consideration: the game played two years ago and the game played recently should count for different weights when recomending a hero. What is more, hero frequency and hero win rate should both play a factor when recommending.
* API to recommend hero based on peers who are slightly better in terms of rank
* API to recommend hero based on existing teammates

### About recommendation engine

* the simple, very naive solution: check player match history and calcalate win rate of each hero. Recommend the one with highest win rate. The most obvious flaw with this is: what if the player plays the hero once and he wins? So we need to filter out those extreme cases.
* so after filtering a few infrequently used heroes, what if some leavers on my team or on their team affected the result? So we need to filter out those cases as well.
* sometimes in a gameplay, the player tried very hard and played very well, KDA stats was good and he lost the game because of some other incident; or the player got high KDAs, but at a cost of teammates' heroes' lives. Win is important, KDA plays a factor as well. So I decided to do a hero and kill, death, assist logistic regression to simulate win/lose and recommend hero based on this model.
* some thoughts that I have but not implemented: the game gets updates and older match should have less influence. Hero frequence should be used as well.
