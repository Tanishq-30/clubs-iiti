from flask import Blueprint, render_template, request, session
from config.mysql import mysql
from utilities.images import img
from utilities.verifyIITIStudent import checkIfMailIsValid

admin = Blueprint('admin', __name__, url_prefix='/clubs')


@admin.route("/<clubName>/<manage>/<email>")
def manage(clubName, manage, email):
    cur = mysql.connection.cursor()
    user = dict(session).get("email", None)
    if(user == None):
        return render_template("signIn.html")
    verified = False
    print("Running query: ", "SELECT Club_Title FROM clubheads WHERE Club_Head_Mail_Id = '{}'".format(
        session["email"]))
    cur.execute(
        f"SELECT Club_Title FROM clubheads WHERE Club_Head_Mail_Id ='{user}'")
    club = cur.fetchall()

    for i in club:
        if (i[0] == clubName):
            verified = True

    if(verified):

        # Remove student from the club
        if(manage == "remove"):
            cur = mysql.connection.cursor()
            cur.execute(
                "select Club_Name FROM clubs WHERE Title='{}'".format(clubName))
            club = cur.fetchone()
            print("Executing Query: " +
                  "DELETE FROM clubMembers WHERE Mail_Id='{}' AND Club_Name='{}';".format(email, club[0]))
            cur.execute("DELETE FROM clubMembers WHERE Mail_Id='{}' AND Club_Name='{}';".format(
                email, club[0]))
            mysql.connection.commit()
            cur.close()
            return redirect("/clubs/{}".format(clubName))

        elif(manage == "approve"):
            cur = mysql.connection.cursor()
            cur.execute(
                "select Club_Name FROM clubs WHERE Title='{}'".format(clubName))
            club = cur.fetchone()
            cur.execute(
                "INSERT INTO clubmembers VALUES ('{}','{}');".format(email, club[0]))
            cur.execute("DELETE FROM approvals WHERE Mail_Id='{}' AND Club_Name='{}';".format(
                email, club[0]))
            cur.execute(
                "DELETE FROM meetings WHERE student_mail_id = '{}' AND host_mail_id = '{}'".format(email, user))
            send_mail(
                email, "Subject:Welcome Welcome!!\n\nCongrats from {}\n You have been accepted into the club!!".format(club[0]))
            mysql.connection.commit()
            cur.close()
            return redirect("/clubs/{}".format(clubName))

        elif(manage == "reject"):
            cur = mysql.connection.cursor()
            cur.execute(
                "select Club_Name FROM clubs WHERE Title='{}'".format(clubName))
            club = cur.fetchone()
            cur.execute("DELETE FROM approvals WHERE Mail_Id='{}' AND Club_Name='{}';".format(
                email, club[0]))
            mysql.connection.commit()
            cur.close()
            return redirect("/clubs/{}".format(clubName))

        elif(manage == "schedule"):
            if(checkIfMailIsValid(email)):
                # msg = "Scheduling Interview with clubhead of " + clubName
                # send_mail(user, "Interview scheduled with student")
                return render_template("interview.html", host=user, student=email, clubName=clubName, meeting_details=["", "", ""])

            else:
                return render_template("error.html")

        else:
            return render_template("error.html")

    else:
        return render_template("error.html")


@admin.route("/<clubName>/edit", methods=['GET', 'POST'])
def edit(clubName):
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        email = dict(session).get("email", None)
        if(email == None):
            return render_template("signIn.html")

        verified = False
        print("Running query: ", "SELECT Club_Title FROM clubheads WHERE Club_Head_Mail_Id = '{}'".format(
            session["email"]))
        cur.execute(
            f"SELECT Club_Title FROM clubheads WHERE Club_Head_Mail_Id ='{email}'")
        club = cur.fetchall()

        for i in club:
            if (i[0] == clubName):
                verified = True

        if(verified):
            print("Running query:",
                  "select Info, Achievements, Events FROM clubs WHERE Title='{}'".format(clubName))
            cur.execute(
                "select Info, Achievements, Events FROM clubs WHERE Title='{}'".format(clubName))
            information = cur.fetchone()
            return render_template("editor.html", info=information[0], achievements=information[1], clubName=clubName, events=information[2])

        else:
            return render_template("error.html")

    else:
        data = request.form
        # print("Fetched form data")
        info = data['info']
        # replace ' with " so that these string does not interfere with our sql queries
        info = info.replace("'", '"')
        achievements = data['achievements']
        achievements = achievements.replace("'", '"')
        events = data['events']
        events = events.replace("'", '"')
        cur = mysql.connection.cursor()
        print("Running query:", "UPDATE clubs SET Info = '{}', Achievements = '{}', Events = '{}' WHERE Title = '{}'".format(
            info, achievements, events, clubName))
        cur.execute("UPDATE clubs SET Info = '{}', Achievements = '{}', Events = '{}' WHERE Title = '{}'".format(
            info, achievements, events, clubName))
        cur.execute(
            "INSERT INTO events VALUES ('{}','{}', NOW());".format(clubName, events))

        mysql.connection.commit()
        cur.close()

        return redirect("/clubs/{}".format(clubName))


@admin.route("/<clubName>/meeting/<student>", methods=["GET", "POST"])
def schedule(clubName, student):

    user = dict(session).get("email", None)
    if(user == None):
        return render_template("signIn.html")

    details = request.form

    verified = False
    cur = mysql.connection.cursor()
    cur.execute(
        f"SELECT Club_Title FROM clubheads WHERE Club_Head_Mail_Id ='{user}'")
    club = cur.fetchall()

    for i in club:
        if (i[0] == clubName):
            verified = True

    if(verified):

        if request.method == "POST":

            details = request.form
            time = details['time']
            time = time[:-3]

            date = details['date']
            date = date.split("/")
            date = date[2]+"-"+date[0]+"-"+date[1]

            link = details['link']
            host = details['host']

            # print(host, student, time, date, link)

            # Insert into db

            send_mail(user, "Subject: Meeting Details\n\nMeeting scheduled with {}\nDetails: \nTime: {}\n Date: {}\n Link: {}".format(
                student, time, date, link))
            send_mail(student, "Subject: Meeting Details\n\nHere are the scheduled meeting details:\nTime: {}\n Date: {}\n Link: {}".format(
                time, date, link))

            cur = mysql.connection.cursor()
            # print("INSERT INTO meetings VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE host_mail_id=%s, student_mail_id=%s, meeting_time=%s, meeting_date=%s, link=%s",
            #     (host, student, time, date, link,
            #         host, student, time, date, link ))
            cur.execute("INSERT INTO meetings VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE host_mail_id=%s, student_mail_id=%s, meeting_time=%s, meeting_date=%s, link=%s",
                        (host, student, time, date, link,
                         host, student, time, date, link))
            cur.execute(
                "UPDATE approvals SET CurrentStatus='A' WHERE Mail_Id='{}'".format(student))
            mysql.connection.commit()
            cur.close()
            # send mails
            return render_template("scheduled.html", student=student, link=link)

        else:
            if(checkIfMailIsValid(student)):
                cur = mysql.connection.cursor()
                cur.execute("SELECT meeting_time, meeting_date, link FROM meetings WHERE host_mail_id = '{}' AND student_mail_id = '{}'".format(
                    user, student))
                meeting_details = cur.fetchone()
                date = str(meeting_details[1])
                # print(date, type(date))
                date = date.split("-")
                date = date[1]+'/'+date[2]+'/'+date[0]
                date = date
                send_mail(user, "Subject: Meeting Updated\n\nMeeting updated with {}\nDetails:\nTime: {}\n Date: {}\n Link: {}".format(
                    student, meeting_details[0], date, meeting_details[2]))
                # print(meeting_details)
                return render_template("interview.html", host=user, student=student, clubName=clubName, meeting_details=meeting_details, date=date)
            else:
                return render_template("error.html")

    else:
        return render_template("error.html")


@admin.route("/<clubName>/<email>")
def detailsOfStudent(clubName, email):
    # check if session['email'] is head of clubName
    user = dict(session).get("email", None)
    if(user == None):
        return render_template("signIn.html")

    verified = False
    cur = mysql.connection.cursor()
    print("Running query: ", "SELECT Club_Title FROM clubheads WHERE Club_Head_Mail_Id = '{}'".format(
        session["email"]))
    cur.execute(
        f"SELECT Club_Title FROM clubheads WHERE Club_Head_Mail_Id ='{user}'")
    club = cur.fetchall()
    cur.execute(f"SELECT * FROM students WHERE Mail_id ='{email}'")
    member = cur.fetchone()
    print("member: ", member)
    for i in club:
        if (i[0] == clubName):
            verified = True
    if(verified):
        return render_template("details.html",
                               email=member[0],
                               name=member[1],
                               link=member[2],
                               branch=member[3],
                               roll=member[4],
                               phone=member[5],
                               yr=member[6], Bio=member[7])
    else:
        return render_template("notAuthorized.html")
