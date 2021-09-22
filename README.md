# FGH-TruckDispatch-System
#### Video Demo:  https://youtu.be/YIcZUqyfxbI
#### Description:

##### Some background

Hi, I am Gevorg Ghukasyan, and this is my final project for the CS50 course. 

I have picked a web-based application as my final project’s technical platform, though I may continue to develop this idea further and make an iOS application which will work in parallel as well.


##### About the application

So this is a very simple fright management system for Truck dispatchers. I have learned from people in the business that many small companies use excel sheets or handwritten notes for organizing the work in their companies. Such notes are used to store information on the delivery and dispatch dates for the freight lots, delivery and dispatch addresses, information on the rates weights, contact information, etc. Although this tool does not promise to be the best solution, still I am sure this may become handy for the business owners and will become a good starting point for further fine tuning to their needs.

##### Main Functionality

1. Load Board

This page shows the freight lots picked by the company and provides wide filtering functionality to the user.

2. New Load

This page is for inputting the information on the freight lots to the system.
Here I have implemented google autocomplete API to ease the process of manual data input and for standardisation for the data. Also google distance matrix service is used to calculate the distance between standardized origin and destination locations and the est duration of the transit.

3. Agents

This page acts as a scoreboard for the company's users where they can see the progress of their colleagues and motivate themselves to higher achievements.

4. Brokers and Carriers 

These sections are designed for adding new partner companies to the fright management system, here we are tracking some necessary information on the companies which are needed for doing business with them.

5. Personal Profile

There is a Personal Profile section for the system users where they can edit some personal information about themselves, including profile photo, contact information, etc.



##### Technical Design

Flask micro web framework for Python is used for the backend side of the application, which is mainly responsible for drawing html pages based on the general layout of the system and specific templates per the system pages.

Sqlite3 is used for storing and accessing information in the system. Sqlite3 db is used also for storing user profiles photos in a base64 encoding. 

Bootstrap 4.5 is used for drawing the web interface of the app.

Ajax and jquery libraries are used for interactions between the font end and the backend of the system 
