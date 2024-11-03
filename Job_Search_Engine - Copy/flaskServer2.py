from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import plotly.graph_objects as go

app = Flask(__name__)

# Configure MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="raj@sql0000",
    database="ai_database"
)

@app.route('/')
def index():
    # Display the form for user input
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    # Get the data from the form input
    search_term = request.form['search_term']
    
    cursor = db.cursor(dictionary=True)
    
    # SQL Query to fetch specific columns from the view with filtering based on input
    query = "SELECT * FROM NYCJobs WHERE `Business Title` LIKE %s OR `Job Description` LIKE %s"
    cursor.execute(query, (f"%{search_term}%", f"%{search_term}%"))
    
    # Fetch all results
    results = cursor.fetchall()
    
    cursor.close()
    
    # Render results.html and pass the results to the template
    return render_template('results.html', results=results, search_term=search_term)

@app.route('/save_row', methods=['POST'])
def save_row():
    # Fetch data from the form
    job_id = request.form['job_id']
    business_title = request.form['business_title']
    agency = request.form['agency']
    positions = request.form['positions']
    level = request.form['level']
    salary_from = request.form['salary_from']
    salary_to = request.form['salary_to']

    jobid = int(job_id)

    # Print values to check if the form data is being received properly
    print(f"Job ID: {job_id}, Title: {business_title}, Agency: {agency}, Positions: {positions}, Level: {level}, Salary From: {salary_from}, Salary To: {salary_to}")
    
    cursor = db.cursor()

    try:
        # Check if job_id already exists
        query = "SELECT COUNT(1) FROM user_prefs WHERE job_id = %s;"
        cursor.execute(query, (jobid,))
        exists = cursor.fetchone()[0]

        if exists == 0:
            print("Job ID is available!")
            try:
                # SQL query to insert the row into user_prefs table
                insert_query = """
                    INSERT INTO user_prefs (job_id, business_title, agency, openings, level, salary_from, salary_to) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s);
                """
                cursor.execute(insert_query, (job_id, business_title, agency, positions, level, salary_from, salary_to))
                
                db.commit()  # Save changes to the database
                print("Data inserted successfully!")
                return redirect(url_for('index'))  # Success redirect

            except Exception as e:
                print(f"Error occurred during insertion: {e}")
                db.rollback()  # Rollback the transaction on error
                return "Error during insertion, transaction rolled back.", 500  # Return HTTP 500
        else:
            print("Job ID already exists!")
            return "Job ID already exists!", 400  # Return HTTP 400 for bad request

    except Exception as e:
        print(f"Error occurred: {e}")
        return "Error occurred while checking job ID.", 500  # Return HTTP 500

    finally:
        cursor.close()

@app.route('/user_Prefs')
def usr_prefs():
    cursor = db.cursor(dictionary=True)
    
    # Call the stored procedure
    cursor.callproc('fetch_unique_jobs')  # Ensure the procedure name matches
    
    # Fetch the result sets from the cursor
    results = []
    for result in cursor.stored_results():
        fetched = result.fetchall()
        #print(f"Fetched {len(fetched)} records.")  # Debugging statement
        results.extend(fetched)
    
    cursor.close()
    
    # Print the results to verify
    #print("Results:", results)  # Debugging statement
    
    # Render the template and pass the results
    return render_template('user_Prefs.html', results=results)

@app.route('/delete_pref', methods=['POST'])
def delete_pref():
    job_id = request.form['job_id']
    business_title = request.form['business_title']
    jobid = int(job_id)  # Convert the string to an integer
    
    print(job_id, business_title)  # For debugging purposes
    
    cursor = db.cursor(dictionary=True)

    # Call the stored procedure with the converted job_id
    cursor.callproc('del_pref', [jobid])

    db.commit()  # Commit the changes

    cursor.close()
    return redirect(url_for('usr_prefs'))


@app.route('/jobs_page')
def jobs_page():
    cursor = db.cursor(dictionary=True)
    
    # Fetch the total number of jobs
    query_total_jobs = "SELECT COUNT(*) AS total_jobs FROM nyc_jobs;"
    cursor.execute(query_total_jobs)
    total_jobs = cursor.fetchone()['total_jobs']
    
    # Fetch the sum of all positions
    query_total_openings = "SELECT SUM(`# of Positions`) AS total_openings FROM nyc_jobs;"
    cursor.execute(query_total_openings)
    total_openings = cursor.fetchone()['total_openings']
    
    # Fetch the minimum Salary expectations
    query_min_sal = "SELECT avg_minimum() AS minimum_sal;"
    cursor.execute(query_min_sal)
    min_salary = cursor.fetchone()['minimum_sal']
    print(f"Minimum salary fetched: {min_salary}")

    # Fetch the Maximum Salary expectations
    query_max_sal = "SELECT avg_maximum() AS maximum_sal;"
    cursor.execute(query_max_sal)
    max_salary = cursor.fetchone()['maximum_sal']
    print(f"Maximum salary fetched: {max_salary}")

    #Recommending Jobs
    # Fetch the business title from user_prefs to find job recommendations
    query_user_prefs = "SELECT business_title FROM user_prefs"
    cursor.execute(query_user_prefs)
    user_prefs = cursor.fetchall()
    
    # Initialize a list to hold all job recommendations
    job_recommendations = []
    
    # For each business title in user preferences, fetch jobs with matching titles
    for user_pref in user_prefs:
        user_business_title = user_pref['business_title']
        
        # Query the nyc_jobs table for similar business titles using LIKE
        query_recommendations = """
            SELECT `Business Title`, `Agency`, `Salary Range From`, `Salary Range To`, `# of Positions`, `level`, `job id`
            FROM nyc_jobs
            WHERE `Business Title` LIKE %s OR `Job Description` LIKE %s
            LIMIT 5
        """


        cursor.execute(query_recommendations, (f"%{user_business_title}%", f"%{user_business_title}%"))
        recommendations = cursor.fetchall()
        
        # Add each set of recommendations to the job_recommendations list
        job_recommendations.extend(recommendations[:5])

        if len(job_recommendations) >= 5:
            break
     
    cursor.callproc('fetch_job_data')

    # Fetch the results from the cursor
    JOBS = []
    for result in cursor.stored_results():
        JOBS = result.fetchall()  # Collect all rows from the procedure's output

    cursor.close()
    print(JOBS)
    # Assuming other variables are defined elsewhere or fetched from the database
    return render_template('Jobs.html', total_jobs=total_jobs, total_openings=total_openings, Min_salary=min_salary, Max_salary=max_salary, job_recommendations=job_recommendations, JOBS=JOBS)
if __name__ == '__main__':
    app.run(debug=True)
