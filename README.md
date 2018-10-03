### Hap.py
# Hap.py Web Application

This repository houses my final project for the Hackbright Academy curriculum. That I developed independently in four weeks.

## Overview

In a world where adults take themselves too seriously and forget to have fun, I decided to make an app that encourages people to be silly using game psychology. 

When you create a profile your information is entered into the database. And you’re directed to the instructions page. 

From there you can go to the homepage to see videos that other users have uploaded. Each video has points associated with it in the database. You can give a video another point which is sent to the server using AJAX, entered into the database, and the value is updated on the page.

This was by far the most challenging feature I made. There were several AJAX calls involved, and a lot of  information being passed around. I also had to make it so that you can’t give the same points multiple times or give yourself points which took a lot of thought. 
 
Every time the home or profile pages are loaded, a query is made to see if points have been added since the last time the table was checked. If you have gotten any, another query is made to see if you leveled up in that category. If you do you’re notified promptly via a flash message. 


Each video has a specific challenge associated with it in the database. If you want to see all the challenges, you can go to this page which is styled with bootstrap. From there you can see all the videos of a given challenge or you can complete it yourself. The video is uploaded using Flask uploads and entered into the database. Then your points are updated accordingly.

If a you want to track your personal progress you can go to the profile page and see it in two easy-to-read graphs made with chartjs. This chart showing the levels is compiled by finding your current levels in the game, and figuring out how many additional points you have based on your overall totals. The chart showing a user’s progress over time is made by joining several tables in a query, finding the time each point is given, then dividing by the number of points required in that level.

I had a lot of fun making this project especially designing the data model.

In the future if I have the opportunity, I’d like to make the game elements more complex and interactive 


<!-- ## Screenshots

![alt text](static/screenshots/01.png "Main page")

![alt text](static/screenshots/02.png "Search")

![alt text](static/screenshots/03.png "Search results")

![alt text](static/screenshots/04.png "Recent searches")

![alt text](static/screenshots/05.png "Previous search") -->