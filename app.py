import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from flask_mail import Mail,Message
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from re import search
from create_table import *
from datetime import datetime
import base64

from helpers import apology, login_required

# Configure application
app = Flask(__name__)
mail = Mail(app)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["MAIL_PASSWORD"] = "Dcor2litty"
app.config["MAIL_SERVER"] = "smtp@gmail.com"
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "friendwoodschools@gmail.com"
mail = Mail(app)
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///fps.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Store site variables
sections = ["Primary","Secondary"]
pry_classes = ["Pry 1","Pry 2","Pry 3","Pry 4","Pry 5","Nur 1", "Nur 2", "Reception", "Kindergatern", 
              "Creche", "Playgroup"]
sec_classes = ["Jss 1","Jss 2","Jss 3","Sss 1", "Sss 2", "Sss 3"]
user_cat = ["Teacher","Parent","Student"]
options = ["YES","NO"]
role = ["Mother","Father"]
relationship = ["Guardian","Parents"]
test_types = ["Exam","Assessment","Evaluation","Mid-Term"]
pry_subjects  = ["Math","English","BST","Quantitative","History", "RNV", "French", "CCA","Prevocational","ICT",
                "Literature", "Verbal-R"]
sec_subjects  = ["Math","English","Chemistry","Physics","History", "Geography", "Accounting", "CRS",
                 "Economics", "Marketing", "Further-Math", "Biology", "Data Processing", "ICT", "Literature",
                 "Civic Education","Social Studies", "BST", "NVE", "Government", "French", "Yoruba", "CCA",
                 "Technical Drawing","Music","Igbo","Animal Husbandry","Hausa"]
roles = ["Admin","Staff"]
terms = ["First Term", "Second Term", "Third Term"]


def p_range(percentages):
    percentages = percentages
    order = set()

    for p in percentages:
        order.add(p)
    return sorted(order,reverse=1)
            



def render_table_header(TABLE_COL_NAMES, pdf, col_widths, align='L'):
    line_height = pdf.font_size * 2
    pdf.set_font(style="B")  # enabling bold text
    i = 0
    for col_name in TABLE_COL_NAMES:
        pdf.cell(col_widths[i], line_height, col_name, border=1, align=align)
        i+= 1
    pdf.ln(line_height)
    pdf.set_font(style="")  # disabling bold text


def render_table_data(TABLE_DATA, pdf, col_widths, align='L'):
    line_height = pdf.font_size * 2
    for _ in range(1):  # repeat data rows
        for row in TABLE_DATA:
            if pdf.will_page_break(line_height):
                render_table_header()
            i = 0
            for datum in row:
                pdf.cell(col_widths[i], line_height, datum, border=1, align=align)
                i+= 1   
            pdf.ln(line_height)

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        if not request.form.get("name") or not request.form.get("password") or not request.form.get("category") or not request.form.get("id"):
            return apology("User input is missing")

        if request.form.get("category") not in user_cat:
            return apology("Input a valid user category")

        if request.form.get("category") == "Teacher":

            # Get data of teacher with such id
            rows = db.execute("SELECT * FROM teachers WHERE id = ?", request.form.get("id"))

            if not rows:
                return apology("There is no such teacher in this branch")

            # Ensure password is correct
            if not check_password_hash(rows[0]["hash"],request.form.get("password")):
                return apology("Invalid Password", 403)

            # Ensure names match
            if request.form.get("name") != rows[0]["name"]:
                return apology("Invalid Username")

            # Remember which user has logged in
            if rows[0]["class"]:
                session["user_class"] = rows[0]["class"]

            session["branch"] = rows[0]["branch"]
            session["user_id"] = int(request.form.get("id"))
            session["user_cat"] = "Teacher"
            session["value"] = 1
            session["name"] = request.form.get("name")
            session["role"] = rows[0]["role"]

            # Redirect user to home page
            return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("unlogged/login.html",user_cat=user_cat)


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if session:
        return redirect("/")
    
    # Validing user's input
    if request.method == "POST":

        # Check if user input contains fullname
        if not request.form.get("f-name") or not request.form.get("m-name") or not request.form.get("l-name") or not request.form.get("email") or not request.form.get("password") or not request.form.get("confirmation") or not request.form.get("key"):
            return apology("User Input missing")

        # Check if both password inputs match
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords don't match")
        
        # Validating schools key
        if request.form.get("key") != "F.P.S00179SCHxyU3422*tyeUdyTEQKVNjndq":
            return apology("Key is not valid")

        fullname = request.form.get("f-name") + " " + request.form.get("m-name") + " " + request.form.get("l-name")

        return render_template("unlogged/register2.html", options=options, sections=sections, pry_classes=pry_classes, sec_classes=sec_classes, fullname=fullname,
                                password=request.form.get("password"),email=request.form.get("email"),roles=roles)
    else:
        return render_template("unlogged/register1.html")

@app.route("/validate", methods=["GET","POST"])
def validate():
    """Validate user's register input"""

    if session:
        return redirect("/")

    if request.method == "GET":
        return redirect("/")

    else:

        # Validate headers
        if not request.form.get("name") or not request.form.get("password") or not request.form.get("email"):
            return apology("Headers Missing")

        # Check if form was filled
        if not request.form.get("img") or not request.form.get("branch") or not request.form.get("option"):
            return apology("Missing Input")

        # Check if branch value is a postive integer
        try:
            branch = int(request.form.get("branch"))
            if not branch > 0:
                return apology("Branch should be a positive integer")
        except:
            return apology("Branch should should be an integer")

        # Check if option is valid
        if request.form.get("option") not in options:
            return apology("Select a valid option")

        # Generate password hash
        hashed = generate_password_hash(request.form.get("password"),method='pbkdf2:sha256')

        if not request.form.get("role") or not request.form.get("role") in roles:
            return apology("Select a valid role")

        if (request.form.get("role") == "Admin" and not request.form.get("ad-key")) or (request.form.get("role") == "Admin" and request.form.get("ad-key") != "Admin-Key"):
            return apology("Enter a valid role")
        
        if request.form.get("option") == "NO":
            user_id = db.execute("INSERT INTO teachers (name,hash,email,branch,image,role) VALUES (?,?,?,?,?,?)",
                            request.form.get("name"),hashed,request.form.get("email"),branch,request.form.get("img"),request.form.get("role"))

        else:
            if not request.form.get("section") or not request.form.get("class") or not request.form.get("key"):
                return apology("Missing input")
                
            # Validating form data for those assigned to classes
            if request.form.get("section") not in sections:
                return apology("Enter a valid section")
            
            user_class = request.form.get("class")

            if request.form.get("key") != "Class-Key":
                return apology("Enter a valid key")

            if request.form.get("section") == "Primary":
                if user_class not in pry_classes:
                    return apology("Enter a valid primary class")
                
            else:
                if user_class not in sec_classes:
                    return apology("Enter a valid secondary class")

            user_id = db.execute("INSERT INTO teachers (name,hash,email,branch,image,class,role) VALUES (?,?,?,?,?,?,?)",
                                request.form.get("name"),hashed,request.form.get("email"),branch,request.form.get("img"),user_class,request.form.get("role"))
                
            session["user_class"] = user_class
            

        
        # Logging user in and caching details
        session["value"] = 0
        session["branch"] = branch
        session["name"] = request.form.get("name")
        session["user_id"] = user_id
        session["user_cat"] = "Teacher"
        session["role"] = request.form.get("role")

        # Displaying user id
        return redirect("/id") 

@app.route("/enquiries",methods=["GET","POST"])
def enquiries():
    if request.method == "GET":
        return render_template("unlogged/enquiries.html")
    else:
        if not request.form.get("name") or not request.form.get("message") or not request.form.get("email") or not request.form.get("number"):
            return apology("Input Missing")
        
        return render_template("unlogged/mes_sent.html")

@app.route("/id")
@login_required
def id_value():

    # Check if user has already viewed id
    if session["value"] == 1:
        return redirect("/")
    else:
        session["value"] = 1

        """Give user id"""
        return render_template("teacher/id.html", user_id=session["user_id"])


@app.route("/", methods=["GET", "POST"])
def index():
    teachers = db.execute("SELECT * FROM teachers LIMIT 12")
 
    """Homepage"""
    if session:
        if session["user_cat"] == "Teacher":
            # Check if the teacher has access to student records
            if "user_class" in session and "branch" in session:
                records = db.execute("SELECT * FROM students WHERE class = ? AND branch = ? ORDER BY name", session["user_class"], session["branch"])

                # Check if there are no students in said class
                if not records:
                    return render_template("index.html")
            
                if request.method == "POST":
                    if request.form.get("progress") == "w-assessment":
                        scores = db.execute("SELECT assessment,name FROM tests WHERE branch = ? AND class = ? AND assessment NOT NULL", session["branch"], session["user_class"])
                        page = "Weekly Assessments"
                        max_score = 10
                        test_type = "assessment"
                        avg_score = db.execute("SELECT AVG(assessment) AS avg FROM tests WHERE branch = ? AND class = ? AND assessment NOT NULL", session["branch"], session["user_class"])

                    elif request.form.get("progress") == "evaluation":
                        page = "Evaluation Tests"
                        scores = db.execute("SELECT eval_test,name FROM tests WHERE branch = ? AND class = ? AND eval_test NOT NULL", session["branch"], session["user_class"])
                        max_score = 20
                        test_type = "eval_test"
                        avg_score = db.execute("SELECT AVG(eval_test) AS avg FROM tests WHERE branch = ? AND class = ? AND eval_test NOT NULL", session["branch"], session["user_class"])
   
                    elif request.form.get("progress") == "mid-tests":
                        page = "Mid-Term Tests"
                        scores = db.execute("SELECT mid_test,name FROM tests WHERE branch = ? AND class = ? AND mid_test NOT NULL", session["branch"], session["user_class"])
                        max_score = 30
                        test_type = "mid_test"
                        avg_score = db.execute("SELECT AVG(mid_test) AS avg FROM tests WHERE branch = ? AND class = ? AND mid_test NOT NULL", session["branch"], session["user_class"])
                    else:
                        page = "Exam Scores"
                        scores = db.execute("SELECT exam,name FROM tests WHERE branch = ? AND class = ? AND exam NOT NULL", session["branch"], session["user_class"])
                        max_score = 70
                        test_type = "exam"
                        avg_score = db.execute("SELECT AVG(exam) AS avg FROM tests WHERE branch = ? AND class = ? AND exam NOT NULL", session["branch"], session["user_class"])
        
                else:
                    scores = db.execute("SELECT assessment,name FROM tests WHERE branch = ? AND class = ? AND assessment NOT NULL", session["branch"], session["user_class"])
                    page = "Weekly Assessments"
                    max_score = 10
                    test_type = "assessment"
                    avg_score = db.execute("SELECT AVG(assessment) AS avg FROM tests WHERE branch = ? AND class = ? AND assessment NOT NULL", session["branch"], session["user_class"])

                # Get number of students
                length = len(records)

                return render_template("teacher/s_progress.html", i=page, scores=scores, max=max_score, type=test_type, no_of_students=length,
                                         avg_score=avg_score)

            else:
                
                return render_template("index.html",teachers=teachers)
            
    return render_template("index.html",teachers=teachers)


@app.route("/about")
#@login_required
def about():
    return render_template("unlogged/about.html")


@app.route("/enroll", methods=["GET", "POST"])
def enroll():
    """Enroll Students"""

    if request.method == "GET":
        return render_template("unlogged/enroll.html", relationship=relationship, role=role,
                                pry_classes=pry_classes, sec_classes=sec_classes)
    
    else:

        # Check for a valid relation
        if not request.form.get("relation") in relationship:
            return apology("Select a valid relation")

        # Check for missing input
        if not request.form.get("number"):
            return apology("Missing Input")

        # Check if branch value was a postive integer
        try:
            number = int(request.form.get("number"))
            if not number > 0:
                return apology("Number of wards should be a positive integer")
        except:
            return apology("Number of wards should be an integer")
        
                    
        # Store ward's data in variables
        f_names = request.form.getlist("f-name")
        passwords = request.form.getlist("password")
        branches = request.form.getlist("branch")
        classes = request.form.getlist("class")
        images = request.form.getlist("img")
        dobs = request.form.getlist("dob")

        # Check if form is incomplete
        if len(images) != number or len(passwords) != number or len(branches) != number or len(f_names) != number or len(classes) != number:
            return apology("Form is incomplete", code=200)

        # Check for missing input for wards
        for i in range(number):
            if not f_names[i] or not passwords[i] or not branches[i] or not classes[i] or not images[i]:
                return apology("Missing input for wards")
                
            # Check if wards branch is a positve integer
            try:
                int(branches[i])
                if not int(branches[i]) > 0:
                    return apology("Wards branch should be a poitive integer")
            except:
                return apology("Wards branch should be an integer")
                
            if not classes[i] in pry_classes and not classes[i] in sec_classes:
                return apology("Enter a valid class")

        if request.form.get("relation") == "Guardian":
            # Check for missing guardian input
            if not request.form.get("guard_name") or not request.form.get("guard_no") or not request.form.get("guard_pass") or not request.form.get("guard_email") or not request.form.get("guard_img"):
                return apology("Missing guardian input")

            # Insert guardian into database
            hashed = generate_password_hash(request.form.get("guard_pass"),method='pbkdf2:sha256')
            guard_id = db.execute("INSERT INTO guardians (name,contact_no,email,hash,image) VALUES (?,?,?,?,?)",request.form.get("guard_name"),request.form.get("guard_no"),
                                  request.form.get("guard_email"),hashed,request.form.get("guard_img"))

            # Insert user data into database
            for i in range(number):
                # Generate password hash
                hashed = generate_password_hash(passwords[i],method='pbkdf2:sha256')
                db.execute("INSERT INTO students (name,contact_no,class,branch,email1,hash,guardian_id,image,dob) VALUES (?,?,?,?,?,?,?,?,?)", f_names[i],
                    request.form.get("guard_no"),classes[i],int(branches[i]),request.form.get("guard_email"),hashed,guard_id,images[i],dobs[i])
        else:
            p_names = request.form.getlist("parent_name")
            p_passwords = request.form.getlist("parent_pass")
            p_numbers = request.form.getlist("parent_no")
            p_emails = request.form.getlist("parent_email")

            if (not p_names[0] and not p_names[1]) or (not p_passwords[0] and not p_passwords[1]) or (not p_numbers[0] and not p_numbers[1]) or (not p_emails[0] and not p_emails[1]):
                return apology("Missing parent input")

            parent_ids = []
            for i in range(len(p_names)):
                if p_names[i]:
                    # Insert parent into database
                    hashed = generate_password_hash(p_passwords[i],method='pbkdf2:sha256')
                    parent_ids.append(db.execute("INSERT INTO parents (name,contact_no,email,hash) VALUES (?,?,?,?)",p_names[i],p_numbers[i],
                                        p_emails[i],hashed))
                                        
            # Insert student data into database
            if len(parent_ids) == 2:
                for i in range(number):
                    # Generate password hash
                    hashed = generate_password_hash(passwords[i],method='pbkdf2:sha256')
                    db.execute("INSERT INTO students (name,contact_no,class,branch,email1,email2,hash,parent1_id,parent2_id,image,dob) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                                f_names[i],p_numbers[0],classes[i],int(branches[i]),p_emails[0],p_emails[1],
                                hashed,parent_ids[0],parent_ids[1],images[i],dobs[i])
            else:
                for i in range(number):
                    # Generate password hash
                    hashed = generate_password_hash(passwords[i],method='pbkdf2:sha256')
                    db.execute("INSERT INTO students (name,contact_no,class,branch,email1,hash,parent1_id,image,dob) VALUES (?,?,?,?,?,?,?,?,?)",
                                f_names[i],p_numbers[0],classes[i],int(branches[i]),p_emails[0],
                                hashed,parent_ids[0],images[i],dobs[i])

        return redirect("/")

@app.route("/grading", methods=["GET","POST"])
@login_required
def grading():
    if session["user_cat"] == "Teacher":
        if request.method == "GET":
            return render_template("teacher/grading.html", sections=sections, pry_classes=pry_classes,
                                     tests=test_types, pry_subjects=pry_subjects, sec_subjects=sec_subjects, sec_classes=sec_classes)
        else:
            if request.form.get("section") not in sections:
                return apology("Enter a valid session")
            
            if request.form.get("test_type") not in test_types:
                    return apology("Enter a valid test type")
            
            subject = request.form.get("subject")
            classs = request.form.get("class")

            if request.form.get("section") == "Primary":
                if subject not in pry_subjects:
                    return apology("Enter a valid primary subject")

                if classs not in pry_classes:
                    return apology("Enter a valid primary class")
                
            else:
                if subject not in sec_subjects:
                    return apology("Enter a valid secondary subject")    

                if  classs not in sec_classes:
                    return apology("Enter a valid secondary class")  
            
            students = db.execute("SELECT * FROM students WHERE class = ? and branch = ?", classs, int(request.form.get("branch")))
            if students:  
                return render_template("teacher/grading2.html", students=students, subject=subject, 
                                        test_type=request.form.get("test_type"),section=request.form.get("section"), sec_classes=sec_classes)
            else:
                return apology("Sorry but no students are in this class")
            
    else:
        return redirect("/")


@app.route("/records", methods=["GET", "POST"])
@login_required
def records():
    if request.method == "POST":

        # Delete student record from database
        if request.form.get("id"):
            db.execute("DELETE FROM students WHERE id = ?", request.form.get("id"))
            db.execute("DELETE FROM tests WHERE id = ?", request.form.get("id"))
            
            if session["user_class"] in pry_classes:
                db.execute("DELETE FROM pry_midterm WHERE id = ?", request.form.get("id"))
                db.execute("DELETE FROM pry_exam WHERE id = ?", request.form.get("id"))
                db.execute("DELETE FROM pry_eval WHERE id = ?", request.form.get("id"))
                db.execute("DELETE FROM pry_assess WHERE id = ?", request.form.get("id"))
            else:
                db.execute("DELETE FROM sec_midterm WHERE id = ?", request.form.get("id"))
                db.execute("DELETE FROM sec_exam WHERE id = ?", request.form.get("id"))
                db.execute("DELETE FROM sec_eval WHERE id = ?", request.form.get("id"))
                db.execute("DELETE FROM sec_assess WHERE id = ?", request.form.get("id"))

        return redirect("/records")
    
    else:
        if session["user_cat"] == "Teacher" and session["role"] == "Staff":
            if "user_class" in session and "branch" in session:
                records = db.execute("SELECT * FROM students WHERE class = ? AND branch = ? ORDER BY name", session["user_class"], session["branch"])

                # Get number of students
                length = len(records)
                return render_template("teacher/records.html", records=records, length=length)

            else:
                return apology("You have no access to this", code=401)

        elif session["user_cat"] == "Teacher" and session["role"] == "Admin":
            records = db.execute("SELECT * FROM students WHERE branch = ?", session["branch"])

            # Get number of students
            length = len(records)
            return render_template("teacher/records.html", records=records, length=length)
        else:
            return redirect("/")



@app.route("/scoring",methods=["GET","POST"])
@login_required
def scoring():
    if session["user_cat"] == "Teacher":
        if request.method == "GET":
            return redirect("/")
        else:

            student_class = request.form.get("class")
            test_type = request.form.get("test_type")
            subject = request.form.get("subject")
            branch = int(request.form.get("branch"))
            section = request.form.get("section")

            # Check if single student's grades where submitted
            if not student_class or not test_type or not subject or not branch or not section:
                return apology("Headers missing")
            
            if section not in sections:
                return apology("Enter valid section")

            student_ids = request.form.getlist("id")
            student_names = request.form.getlist("name")
            scores = request.form.getlist("score")

            # Store the number of students in a class
            no_of_students = len(db.execute("SELECT * FROM students WHERE class = ? AND branch = ?", student_class,branch))

            # Check if all students details was submitted
            if student_class in pry_classes:
                if len(student_ids) != no_of_students or len(student_names) != no_of_students or len(scores) != no_of_students:
                    return apology("Student Data Incomplete")

                for i in range(no_of_students):
                    if not student_ids[i] or not student_names[i] or not scores[i]:
                        return apology("Student input is missing")
                
            if section == "Primary":
                for i in range(no_of_students):
                    if test_type == "Assessment":
                        s_id = db.execute("SELECT name FROM pry_assess WHERE student_id = ? AND subject = ?",student_ids[i],subject)
                    elif test_type == "Evaluation":
                        s_id = db.execute("SELECT name FROM pry_eval WHERE student_id = ? AND subject = ?",student_ids[i],subject)
                    elif test_type == "Mid-Term":
                        s_id = db.execute("SELECT name FROM pry_midterm WHERE student_id = ? AND subject = ?",student_ids[i],subject)
                    else:
                        s_id = db.execute("SELECT name FROM pry_exam WHERE student_id = ? AND subject = ?",student_ids[i],subject)
 
                    if s_id:
                        return apology("Student scores for this subject have already been submitted")

                for i in range(no_of_students):
                    
                    # Check if user already has row in database
                    student_id = db.execute("SELECT student_id FROM tests WHERE student_id = ?", student_ids[i])
                    if not student_id:
                        db.execute("INSERT INTO tests (student_id,class,branch,name) VALUES (?,?,?,?)",student_ids[i],student_class,branch,student_names[i])
                            
                    if test_type == "Assessment":

                        # Insert data into tests
                        values = db.execute("SELECT assessment FROM tests WHERE student_id = ?", student_ids[i])
                        if values[0]["assessment"] is not None:
                            db.execute("UPDATE tests SET assessment = ? WHERE student_id = ?", values[0]["assessment"] + int(scores[i]), student_ids[i])   
                        else:
                            db.execute("UPDATE tests SET assessment = ? WHERE student_id = ?",int(scores[i]), student_ids[i]) 

                        db.execute("INSERT INTO pry_assess (student_id,subject,score,name,branch,class) VALUES (?,?,?,?,?,?)", 
                                    student_ids[i],subject,int(scores[i]),student_names[i],branch,student_class)  
                        

                    elif test_type == "Evaluation":

                        # Insert data into tests
                        values = db.execute("SELECT eval_test FROM tests WHERE student_id = ?", student_ids[i])
                        if values[0]["eval_test"] is not None:
                            db.execute("UPDATE tests SET eval_test = ? WHERE student_id = ?", values[0]["eval_test"] + int(scores[i]), student_ids[i])   
                        else:
                            db.execute("UPDATE tests SET eval_test = ? WHERE student_id = ?",int(scores[i]), student_ids[i]) 

                        db.execute("INSERT INTO pry_eval (student_id,subject,score,name,branch,class) VALUES (?,?,?,?,?,?)", 
                                    student_ids[i],subject,int(scores[i]),student_names[i],branch,student_class) 

                    elif test_type == "Mid-Term":
                        
                        # Insert data into tests
                        values = db.execute("SELECT mid_test FROM tests WHERE student_id = ?", student_ids[i])
                        if values[0]["mid_test"] is not None:
                            db.execute("UPDATE tests SET mid_test = ? WHERE student_id = ?", values[0]["mid_test"] + int(scores[i]), student_ids[i])   
                        else:
                            db.execute("UPDATE tests SET mid_test = ? WHERE student_id = ?",int(scores[i]), student_ids[i]) 

                        db.execute("INSERT INTO pry_midterm (student_id,subject,score,name,branch,class) VALUES (?,?,?,?,?,?)", 
                                    student_ids[i],subject,int(scores[i]),student_names[i],branch,student_class)   
                        
                    else:

                        # Insert data into tests
                        values = db.execute("SELECT exam FROM tests WHERE student_id = ?", student_ids[i])
                        if values[0]["exam"] is not None:
                            db.execute("UPDATE tests SET exam = ? WHERE student_id = ?", values[0]["exam"] + int(scores[i]), student_ids[i])   
                        else:
                            db.execute("UPDATE tests SET exam = ? WHERE student_id = ?",int(scores[i]), student_ids[i]) 

                        db.execute("INSERT INTO pry_exam (student_id,subject,score,name,branch,class) VALUES (?,?,?,?,?,?)", 
                                    student_ids[i],subject,int(scores[i]),student_names[i],branch,student_class)
                return redirect("/grading")
            else:
                for i in range(no_of_students):
                    if test_type == "Assessment":
                        s_id = db.execute("SELECT name FROM sec_assess WHERE student_id = ? AND subject = ?",student_ids[i],subject)
                    elif test_type == "Evaluation":
                        s_id = db.execute("SELECT name FROM sec_eval WHERE student_id = ? AND subject = ?",student_ids[i],subject)
                    elif test_type == "Mid-Term":
                        s_id = db.execute("SELECT name FROM sec_midterm WHERE student_id = ? AND subject = ?",student_ids[i],subject)
                    else:
                        s_id = db.execute("SELECT name FROM sec_exam WHERE student_id = ? AND subject = ?",student_ids[i],subject)
 
                    if s_id:
                        return apology("Student scores for this subject have already been submitted")

                for i in range(no_of_students):
                    
                    # Check if user already has row in database
                    student_id = db.execute("SELECT student_id FROM tests WHERE student_id = ?", student_ids[i])
                    if not student_id:
                        db.execute("INSERT INTO tests (student_id,class,branch,name) VALUES (?,?,?,?)",student_ids[i],student_class,branch,student_names[i])

                    if scores[i]:
                        if test_type == "Assessment":

                            # Insert data into tests
                            values = db.execute("SELECT assessment FROM tests WHERE student_id = ?", student_ids[i])
                            if values[0]["assessment"] is not None:
                                db.execute("UPDATE tests SET assessment = ? WHERE student_id = ?", values[0]["assessment"] + int(scores[i]), student_ids[i])   
                            else:
                                db.execute("UPDATE tests SET assessment = ? WHERE student_id = ?",int(scores[i]), student_ids[i]) 

                            db.execute("INSERT INTO sec_assess (student_id,subject,score,name,branch,class) VALUES (?,?,?,?,?,?)", 
                                        student_ids[i],subject,int(scores[i]),student_names[i],branch,student_class)  
                            

                        elif test_type == "Evaluation":

                            # Insert data into tests
                            values = db.execute("SELECT eval_test FROM tests WHERE student_id = ?", student_ids[i])
                            if values[0]["eval_test"] is not None:
                                db.execute("UPDATE tests SET eval_test = ? WHERE student_id = ?", values[0]["eval_test"] + int(scores[i]), student_ids[i])   
                            else:
                                db.execute("UPDATE tests SET eval_test = ? WHERE student_id = ?",int(scores[i]), student_ids[i]) 

                            db.execute("INSERT INTO sec_eval (student_id,subject,score,name,branch,class) VALUES (?,?,?,?,?,?)", 
                                        student_ids[i],subject,int(scores[i]),student_names[i],branch,student_class) 

                        elif test_type == "Mid-Term":
                            
                            # Insert data into tests
                            values = db.execute("SELECT mid_test FROM tests WHERE student_id = ?", student_ids[i])
                            if values[0]["mid_test"] is not None:
                                db.execute("UPDATE tests SET mid_test = ? WHERE student_id = ?", values[0]["mid_test"] + int(scores[i]), student_ids[i])   
                            else:
                                db.execute("UPDATE tests SET mid_test = ? WHERE student_id = ?",int(scores[i]), student_ids[i]) 

                            db.execute("INSERT INTO sec_midterm (student_id,subject,score,name,branch,class) VALUES (?,?,?,?,?,?)", 
                                        student_ids[i],subject,int(scores[i]),student_names[i],branch,student_class)   
                            
                        else:
                            # Insert data into tests
                            values = db.execute("SELECT exam FROM tests WHERE student_id = ?", student_ids[i])
                            if values[0]["exam"] is not None:
                                db.execute("UPDATE tests SET exam = ? WHERE student_id = ?", values[0]["exam"] + int(scores[i]), student_ids[i])   
                            else:
                                db.execute("UPDATE tests SET exam = ? WHERE student_id = ?",int(scores[i]), student_ids[i]) 

                            db.execute("INSERT INTO sec_exam (student_id,subject,score,name,branch,class) VALUES (?,?,?,?,?,?)", 
                                        student_ids[i],subject,int(scores[i]),student_names[i],branch,student_class)

                #nesgroup.org/28
                return redirect("/grading")
    else:
        return redirect("/")


@app.route("/reset", methods=["GET","POST"])
def reset():
    return render_template("unlogged/reset.html", user_cat=user_cat)


@app.route("/results", methods=["GET","POST"])   
@login_required
def results():
    if request.method == "GET":
        if session["user_cat"] != "Teacher":
            return redirect("You are unauthorised to view this")

        if not request.args.get("option"):
            return render_template("teacher/results.html", user_cat=user_cat, terms=terms, test_types=test_types)

        elif request.args.get("option") == "release":
            if session["role"] != "Admin":
                return apology("You are not the schools admin")
            return redirect("/")

        elif request.args.get("option") == "generate":
            if session["role"] != "Admin":
                return apology("You are not the schools admin")
            
            if not request.args.get("term") in terms or not request.args.get("test_type") in test_types:
                return apology("Enter a valid input")
            
            if not request.args.get("address") or not request.args.get("contact") or not request.args.get("pmidterm") or not request.args.get("pexam") or not request.args.get("sexam") or not request.args.get("smidterm"):
                return apology("Input missing", code=200)
            
            # Store PDF Headers
            term_session = "2022-2023"
            term = request.args.get("term").upper()
            test_type = request.args.get("test_type").upper()
            title = "EVALUATION REPORT SLIP"
            date = f"{datetime.now()}"
            address = request.args.get("address").upper()
            email = "friendswoodschools@gmail.com"
            description = f"{term_session}, {term} {test_type} RESULT"


            for primary in pry_classes:
                percentages =[]
                class_data = []
                # Get number of students in class
                students = db.execute("SELECT * FROM students where class = ? ", primary) 
                for student in students:
                    if student:
                        # Store table information
                        header = ["Name", f"{student['name']} ", "Postion", " "]

                        if student["email1"] and student["email2"]:
                            data = [
                                ["Gender", " ", " ", " "],
                                ["DOB", student["dob"], "Grand Total Score", " "], # 'testing','size'],
                                ["Class", primary, "Percentage", " "], # 'testing','size'],
                                ["Reg No", f"{student['id']}", " ", " "],
                                ["Email", student['email1'] + ", " + student["email2"], "Result Summary", " "] # 'testing','size'],
                            ]
                        elif student["email1"]:
                            data = [
                                ["Gender", " ", " ", " "],
                                ["DOB", student["dob"], "Grand Total Score", " "], # 'testing','size'],
                                ["Class", primary, "Percentage", " "], # 'testing','size'],
                                ["Reg No", f"{student['id']}", " ", " "],
                                ["Email", student['email1'], "Result Summary", " "] # 'testing','size'],
                            ]
                        else:
                            data = [
                                ["Gender", " ", " ", " "],
                                ["DOB", student["dob"], "Grand Total Score", " "], # 'testing','size'],
                                ["Class", primary, "Percentage", " "], # 'testing','size'],
                                ["Reg No", f"{student['id']}", " ", " "],
                                ["Email", student['email2'] + ", " + student["email2"], "Result Summary", " "] # 'testing','size'],
                            ]

                            

                        header2 = ["#","Subject","Obtained","Obtainable", "Obtained","Obtainable","Total","Grade","Grade Remarks"]
                        
                        # Add students grades
                        sums = [" "," ",0,0,0,0,0," "," "]
                        len_subjects = 0
                        grades = []
                        for subject in range(len(pry_subjects)):
                            midterm_score = db.execute("SELECT score FROM pry_midterm WHERE student_id = ? AND subject = ?", student["id"], pry_subjects[subject])
                            exam_score = db.execute("SELECT score FROM pry_exam WHERE student_id = ? AND subject = ?", student["id"], pry_subjects[subject])

                            if midterm_score and exam_score:
                                len_subjects += 1
                                midterm_score = midterm_score[0]["score"]
                                exam_score = exam_score[0]["score"]
                                total = exam_score + midterm_score
                                if total >= 70:
                                    remark = "Excellent"
                                    grade = "A"
                                elif total >= 60 and total <= 69:
                                    remark = "Very Good"
                                    grade = "B"
                                elif total >= 50 and total <= 59:
                                    remark = "Good"
                                    grade = "C"
                                elif total >= 40 and total <= 49:
                                    remark = "Pass"
                                    grade = "D"
                                else:
                                    remark = "Fail"
                                    grade = "F"

                                max_mid = request.args.get("smidterm")
                                max_exam = request.args.get("sexam")

                                # Store total sum of all score
                                if len(grade) == 0:
                                    sums[2] = int(midterm_score)
                                    sums[3] = int(max_mid)
                                    sums[4] = int(exam_score)
                                    sums[5] = int(max_exam)
                                    sums[6] = total

                                else:
                                    sums[2] += int(midterm_score)
                                    sums[3] += int(max_mid)
                                    sums[4] += int(exam_score)
                                    sums[5] += int(max_exam)
                                    sums[6] += total

                                scores = [f"{len(grades) + 1}",pry_subjects[subject],f"{midterm_score}",max_mid, f"{exam_score}", max_exam,f"{total}",grade, remark]
                                grades.append(scores)

                        # Make all the list items strings
                        for sum in range(len(sums)):
                            sums[sum] = f"{sums[sum]}"
                        
                        if len_subjects != 0:
                            grades.append(sums)

                        if (int(sums[5]) + int(sums[3])) == 0:
                            percentage = round(0 * 100, 2)
                        else: 
                       
                            percentage = round((int(sums[6]) / (int(sums[5]) + int(sums[3]))) * 100, 2)

                        if percentage >= 70:
                            data[4][3] = "Excellent"
                        elif percentage >= 60 and percentage <= 69:
                            data[4][3] = "Very Good"
                        elif percentage >= 50 and percentage <= 59:
                            data[4][3] = "Good"
                        elif percentage >= 40 and percentage <= 49:
                            data[4][3] = "Pass"
                        else:
                            data[4][3] = "Fail"

                        data[1][3] = sums[6] + " / " + f"{(int(sums[5]) + int(sums[3]))}"
                        data[2][3] = f"%{percentage}"
                        class_data.append([header,data,header2,grades,percentage])
                        percentages.append(percentage)
                

                i = 0
                for student in students:
                    if student:
                        prange = p_range(percentages)
                        for p in range(len(prange)):
                            if class_data[i][4] == prange[p]:
                                position = class_data[i][0]
                                position[3] = f"{p + 1}"
                                

                        # Create PDF object
                        pdf = PDF(orientation='P', unit='mm', format='A4')

                        # Set PDF properties
                        pdf.set_draw_color(191,191, 191)
                        pdf.set_title(title)
                        pdf.set_author('FPS')
                        pdf.set_auto_page_break(auto=True, margin = 2)

                        # Create page and add header
                        pdf.add_page()
                        pdf.head(title= title, email= email, date= date, address= address)

                        """
                        fonts(times, courier, helvetica, symbol, zpfdingbats)
                        """
                        # Create tables
                        col_widths = [20,100,50,20]  
                        pdf.set_font("helvetica","",11)
                        pdf.cell(0,10,description, ln=1, align='C')
                        pdf.set_font_size(9)
                        render_table_header(class_data[i][0],pdf,col_widths)
                        render_table_data(class_data[i][1], pdf, col_widths)

                        pdf.ln()
                        col_widths = [10,40,20,20,20,20,20,10,30]  
                        render_table_header(class_data[i][2],pdf,col_widths,'C')
                        render_table_data(class_data[i][3], pdf, col_widths,'C')

                        #pdf.create_table(table_data = data2, cell_width='even')
                        pdf.ln()
                        #pdf.create_table(table_data = grades, cell_width='uneven')

                        # Open Grade Key file
                        pdf.set_font("helvetica","B",8)
                        with open("Document.txt", "rb") as file:
                            file = file.read().decode("latin-1")
                            pdf.multi_cell(80,5,file,border=1)
                        pdf.ln()

                        width = (60/100) * pdf.w
                        pdf.set_font_size(9)
                        pdf.cell(0,10,"Class Teacher's Comment: ", ln=True)
                        pdf.cell(width,10,"Class Teacher: ",)
                        pdf.cell(pdf.w - width,10,"Teacher's Signature: ",ln=True)

                        pdf.cell(0,10,"Principal's Comment: ", ln=True)
                        pdf.cell(width,10,"Principal: ",)
                        pdf.cell(pdf.w - width,10,"Principal's's Signature: ",ln=True)
                        pdf.output(f"{primary} {student['name']}.pdf")
                        i += 1

            for secondary in sec_classes:
                percentages =[]
                class_data = []
                # Get number of students in class
                students = db.execute("SELECT * FROM students where class = ? ", secondary) 
                for student in students:
                    if student:
                        # Store table information
                        header = ["Name", f"{student['name']} ", "Postion", " "]

                        if student["email1"] and student["email2"]:
                            data = [
                                ["Gender", " ", " ", " "],
                                ["DOB", student["dob"], "Grand Total Score", " "], # 'testing','size'],
                                ["Class", primary, "Percentage", " "], # 'testing','size'],
                                ["Reg No", f"{student['id']}", " ", " "],
                                ["Email", student['email1'] + ", " + student["email2"], "Result Summary", " "] # 'testing','size'],
                            ]
                        elif student["email1"]:
                            data = [
                                ["Gender", " ", " ", " "],
                                ["DOB", student["dob"], "Grand Total Score", " "], # 'testing','size'],
                                ["Class", primary, "Percentage", " "], # 'testing','size'],
                                ["Reg No", f"{student['id']}", " ", " "],
                                ["Email", student['email1'], "Result Summary", " "] # 'testing','size'],
                            ]
                        else:
                            data = [
                                ["Gender", " ", " ", " "],
                                ["DOB", student["dob"], "Grand Total Score", " "], # 'testing','size'],
                                ["Class", primary, "Percentage", " "], # 'testing','size'],
                                ["Reg No", f"{student['id']}", " ", " "],
                                ["Email", student['email2'] + ", " + student["email2"], "Result Summary", " "] # 'testing','size'],
                            ]

                        header2 = ["#","Subject","Obtained","Obtainable", "Obtained","Obtainable","Total","Grade","Grade Remarks"]
                        
                        # Add students grades
                        sums = [" "," ",0,0,0,0,0," "," "]
                        len_subjects = 0
                        grades = []
                        for subject in range(len(sec_subjects)):
                            midterm_score = db.execute("SELECT score FROM sec_midterm WHERE student_id = ? AND subject = ?", student["id"], sec_subjects[subject])
                            exam_score = db.execute("SELECT score FROM sec_exam WHERE student_id = ? AND subject = ?", student["id"], sec_subjects[subject])

                            if midterm_score and exam_score:
                                len_subjects += 1
                                midterm_score = midterm_score[0]["score"]
                                exam_score = exam_score[0]["score"]
                                total = exam_score + midterm_score
                                if total >= 70:
                                    remark = "Excellent"
                                    grade = "A"
                                elif total >= 60 and total <= 69:
                                    remark = "Very Good"
                                    grade = "B"
                                elif total >= 50 and total <= 59:
                                    remark = "Good"
                                    grade = "C"
                                elif total >= 40 and total <= 49:
                                    remark = "Pass"
                                    grade = "D"
                                else:
                                    remark = "Fail"
                                    grade = "F"

                                max_mid = request.args.get("smidterm")
                                max_exam = request.args.get("sexam")

                                # Store total sum of all score
                                if len(grade) == 0:
                                    sums[2] = int(midterm_score)
                                    sums[3] = int(max_mid)
                                    sums[4] = int(exam_score)
                                    sums[5] = int(max_exam)
                                    sums[6] = total

                                else:
                                    sums[2] += int(midterm_score)
                                    sums[3] += int(max_mid)
                                    sums[4] += int(exam_score)
                                    sums[5] += int(max_exam)
                                    sums[6] += total

                                scores = [f"{len(grades) + 1}",sec_subjects[subject],f"{midterm_score}",max_mid, f"{exam_score}", max_exam,f"{total}",grade, remark]
                                grades.append(scores)

                        # Make all the list items strings
                        for sum in range(len(sums)):
                            sums[sum] = f"{sums[sum]}"
                        
                        if len_subjects != 0:
                            grades.append(sums)

                        if (int(sums[5]) + int(sums[3])) == 0:
                            percentage = round(0 * 100, 2)
                        else: 
                            percentage = round((int(sums[6]) / (int(sums[5]) + int(sums[3]))) * 100, 2)
                        
                        if percentage >= 70:
                            data[4][3] = "Excellent"
                        elif percentage >= 60 and percentage <= 69:
                            data[4][3] = "Very Good"
                        elif percentage >= 50 and percentage <= 59:
                            data[4][3] = "Good"
                        elif percentage >= 40 and percentage <= 49:
                            data[4][3] = "Pass"
                        else:
                            data[4][3] = "Fail"
                            
                        data[1][3] = sums[6] + " / " + f"{(int(sums[5]) + int(sums[3]))}"
                        data[2][3] = f"%{percentage}"
                        class_data.append([header,data,header2,grades,percentage])
                        percentages.append(percentage)
                

                i = 0
                for student in students:
                    if student:

                        prange = p_range(percentages)

                        for p in range(len(prange)):
                            if class_data[i][4] == prange[p]:
                                position = class_data[i][0]
                                position[3] = f"{p + 1}"

                        # Create PDF object
                        pdf = PDF(orientation='P', unit='mm', format='A4')

                        # Set PDF properties
                        pdf.set_draw_color(191,191, 191)
                        pdf.set_title(title)
                        pdf.set_author('FPS')
                        pdf.set_auto_page_break(auto=True, margin = 2)

                        # Create page and add header
                        pdf.add_page()
                        pdf.head(title= title, email= email, date= date, address= address)

                        """
                        fonts(times, courier, helvetica, symbol, zpfdingbats)
                        """
                        # Create tables
                        col_widths = [20,100,50,20]  
                        pdf.set_font("helvetica","",11)
                        pdf.cell(0,10,description, ln=1, align='C')
                        pdf.set_font_size(9)
                        render_table_header(class_data[i][0],pdf,col_widths)
                        render_table_data(class_data[i][1], pdf, col_widths)

                        pdf.ln()
                        col_widths = [10,40,20,20,20,20,20,10,30]  
                        render_table_header(class_data[i][2],pdf,col_widths,'C')
                        render_table_data(class_data[i][3], pdf, col_widths,'C')

                        #pdf.create_table(table_data = data2, cell_width='even')
                        pdf.ln()
                        #pdf.create_table(table_data = grades, cell_width='uneven')

                        # Open Grade Key file
                        pdf.set_font("helvetica","B",8)
                        with open("Document.txt", "rb") as file:
                            file = file.read().decode("latin-1")
                            pdf.multi_cell(80,5,file,border=1)
                        pdf.ln()

                        width = (60/100) * pdf.w
                        pdf.set_font_size(9)
                        pdf.cell(0,10,"Class Teacher's Comment: ", ln=True)
                        pdf.cell(width,10,"Class Teacher: ",)
                        pdf.cell(pdf.w - width,10,"Teacher's Signature: ",ln=True)

                        pdf.cell(0,10,"Principal's Comment: ", ln=True)
                        pdf.cell(width,10,"Principal: ",)
                        pdf.cell(pdf.w - width,10,"Principal's's Signature: ",ln=True)
                        pdf.output(f"{secondary} {student['name']}.pdf")
                        i += 1
            return redirect("/register")

        else:
            return apology("Come here the right way")

@app.route("/settings", methods=["GET","POST"])   
def settings():
    if request.method == "GET":
        if not request.args.get("option"):
            return render_template("unlogged/security.html")
        elif request.args.get("option") == "payment":
            return render_template("unlogged/payment.html")
        elif request.args.get("option") == "security":
            return render_template("unlogged/security.html")
        elif request.args.get("option") == "account-type":
            return render_template("unlogged/acc-type.html")
        else:
            return apology("Enter a valid option")






