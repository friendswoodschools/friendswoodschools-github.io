# FPS (FRIENDSWOOD PRIVATE SCHOOLS)
#### Video Demo:  https://youtu.be/1fp_2tMIvmc
#### Description: This is a simply a website designed in mind for a school, here on the website teachers,students and parents have various features accessible to them
but as of submitting this project only most of the teachers features have been implemented so this project is merely a prototype as I still plan on working on the site.
The website can be used by teachers to manage student records, grade tests, study the progress of the students and also generate student report cards along with other
features. It also helps to provide information to those interested in getting admission for their wards and raise awareness on the services that the school provides as
well as providing a medium for communication with the school's administration.


# Main folder:
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

app.py - In this file is where we have the backend program for our server as well as additional verifications of forms on our site. It includes the programs for individual 
routes and also links in our database to our web program.

helpers.py - Include additional functions used in app.py.

-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
## Static folder - contains all artwork and logos on the site.

-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

## Templates folder: - contains all html templates

index.html - contains the markup syntax for the homepage.
apology.html - contains the layout for an apology in case of errors or mistakes made in forms
layout.html - contains the main layout of most templates such as the styles used and imported as well as the main designs of the site.
layout2.html - contains the main layout of most templates such as the styles used and imported as well as the main designs of the site excluding the header and footer.

### unlogged folder - contains all templates seen when not logged in on site


register1.html - on this page is where a teacher completes the first stage of registering.
register2.html - on this page is where a teacher completes the last stage of registering.

<---Thought process on writing the register page--->

When writing the register page I wanted the user to register with their fullname as the teachers and students will be identified by their names although it's very common for 
people to have the same names so I decided to ask for the users full but I was well aware some users would not put in their fullname
so in order to make sure their fullnames were entered I split the form to recieve both the firstname, middlename and lastname. All the same
the users fullname still cannot be a unique constraint so instead of using unique usernames I allowed users to login with their id's. Also when making sure only teachers
could register on the site I needed to make sure that they could input something only teachers would be able to know. For this I utilized keys on the site to make sure
that the people registering were infact teachers of the school.


login.html - on this page is where a user has the ability to login into his or her account on the site whether it be has a teacher, students or any other user category.
about.html - this page contains and displays information about the mission and goals of the school and in general contains information about the school.
enquiries.html - this page provides a medium for communicating with the schools administrator, it also informs the viewer on ways to communicate with us.
mes_sent.html - this page is displayed after a user has successfully sent a message to the school administrator.
enroll.html - on this page students can be enrolled in the school into any available classes.
reset.html - on this page the user has the ability to reset his/her password.

acc-type.html  ----------------.                               
payment.html                   |-----STILL UNDER DEVELOPMENT 
security.html  ----------------.

###teacher folder - contains all templates seen when logged in as a teacher

s-progress.html - this is homepage layout for teachers. On this page information is displayed about students progress in a particular class if a teacher was assigned to
that class.

<---Thought process on writing the progress homepage--->

I needed to make sure that only teachers assigned to classes access to view student progress in a class for this I added additional layers of verification on that 
page

records.html - Displays records of students in a class if the teacher is assigned to a class and if user is registered as an admin the page displays records of all
students in school.

<---Thought process on writing the records page--->

I needed to make sure that only teachers assigned to classes or the admin had access to manage student records for this I added additional layers of verification on that 
page

grading1.html - on this page is where a teacher takes the first steps in grading student test by filling in the form to configure the next page.
grading2.html - on this page is where a teacher inputs scores for student's tests.

<---Thought process on writing the grading page--->

I needed to make sure that only teachers could only input scores once so I added a checker to see if scores for a particular subject, class and branch had been submitted 
previously.

results.html - on this page is where the admin can generate and release student results.
id.html - this page can only be viewed once and displays the users id.


<---Thought process on writing the id page--->

I needed to make sure that users could only view the id page once since if they refreshed the page it would register the user and continue inserting them into the database
for this I added another checker to see if the user had already viewed the id page

<---Thanks for the opportunity---> <---This was CS50--->

