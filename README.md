## README.md

### by Alex Holyk

### Project Architecture

This program combines a back-end API that creates movie review sentiment analysis predictions (positive or negative), which was trained on IMDB data, with a front-end streamlit dashboard that compares the distributions of reviews between testing and training data, and distribution of positive/negative reviews between testing and training data. At the bottom it shows accuracy and precision, among other stats. The dashboard also allows you to test on new reviews, and updates the charts and stats accordingly. In this final version of the project, we integrate CI/CD and testing. You can run `pytest` on the local command line for local testing, and the ci.yml file implements linting and testing on pull requests in github. Included are directions for running the API and dashboard on AWS EC2.

### Local Development: how to clone and run locally in Docker (PRIOR VERSION; CHECK CONTINUED VALIDITY):

- On command line, run: git clone `https://github.com/alexanderholyk/ML_with_CICD_and_testing`

- Switch into the folder: `cd ML_with_CICD_and_testing` or similar

- Optional: run command `make build`. If you skip this, it will be called anyway by the next step

- On command line, run: `make run` to run a container. This will show URLs for the API and Dashboard; you can copy and paste these into the browser. Alternatively, after calling `make run` you can open Postman, choose your method and endpoint (e.g. http://127.0.0.1:8000/predict), and test it that way. But the intention is to focus on the streamlit dashboard, so follow that URL and you can compare the training and inference distributions and metrics.

- To terminate the program, on command line press `ctrl + c`, or you can just skip to `make clean` to delete the image and keep your system clean.

### Manual Deployment Guide

TODO: make it very detailed. A step-by-step guide for a new developer to deploy this project from scratch. This must include:

- How to launch and configure the EC2 instance and its security group.

- All the commands needed to install dependencies (Git, Docker) on the server.

- The exact docker commands to create the volume, build the images, and run the two containers in detached mode.

1. Access AWS. The Chrome brower works, but Safari can be problematic. In class, we accessed the sandbox through https://awsacademy.instructure.com/login/canvas (log in) > Modules > AWS Academy Learner Lab > Launch AWS Academy Learner Lab. Click Start Lab. Wait a couple minutes for the yellow circle to turn green. When it does, click AWS by the green dot to get to the Console Home.

2. Start an EC2 instance:  
    - Launch a new t2.micro EC2 instance with Ubuntu.
        1. Click the magnifying glass in the top to search for ec2, then select it. 
        2. Click Launch instance. Name it how you like (I'm choosing assignment_6_server). 
        3. Under Quick Start, select Ubuntu and keep the default AMI. 
        4. Switch Instance Type to t2.micro.
        5. Under Key pair name, select vockey.
        6. Under Network settings, click Edit.
        7. Change security group name to asst_6_security_group, and Description to "SSH FastAPI and Streamlit access".  
        8. Under Security group rule 1, change source type to My IP. Under Description, write "SSH for admin". Click Add security group rule.
        NOTE: I revised source type from My IP to Anywhere, as this was preventing me from connecting to the instance.
        9. Under Security group rule 2, keep Type as Custom TCP. Type 8000 in Port range. Change source type to Anywhere. Under Description, write "FastAPI". Click Add security group rule.
        10. Under Security group rule 2, keep Type as Custom TCP. Type 8501 in Port range. Change source type to Anywhere. Under Description, write "Streamlit".
        11. Click Launch instance at the bottom of the page. After a few seconds, go back to Instances in the left-hand menu, where you should see your instance starting up (state = pending, then running.)

3. Connect to your EC2 instance using SSH.
    - Select your instance, and click Connect at the top.
    - Keep the default settings, and click Connect in the bottom right.

4. Set up the Server Environment. On the EC2 instance, install Docker and Git:
    - Update packages for Ubuntu:
        `sudo apt_get update -y`
        `sudo apt_get upgrade -y`

    - Install Docker and Git, and enable Docker. This will also let the ubuntu user run docker without sudo:
        `sudo apt-get install -y docker.io git`
        `sudo systemctl enable --now docker`
        `sudo usermod -aG docker $USER`
        `newgrp docker`

5. Deploy the Application:
    - Clone the GitHub repository onto the EC2 instance:
        `cd ~`
        `git clone https://github.com/alexanderholyk/ML_with_CICD_and_testing.git`
        `cd ML_with_CICD_and_testing`

    - Create a shared Docker volume for the logs.
        `docker network create sentinet || true`
        `docker volume  create sentiment_logs || true`

    - Build the Docker images for both the api and monitoring services.
        `docker build -f api/Dockerfile        -t sentiment-api .`
        `docker build -f monitoring/Dockerfile -t sentiment-monitor .`

    - Run both containers in detached mode (-d), ensuring they are connected to the shared volume.
        `docker rm -f sentiment_api sentiment_monitor >/dev/null 2>&1 || true`
        Run the API:
        `docker run -d --name sentiment_api --network sentinet -v sentiment_logs:/app/logs -p 8000:8000 sentiment-api`
        Give the API around 5 seconds to start.
        Then run the Streamlit dashboard:
        `docker run -d --name sentiment_monitor --network sentinet -v sentiment_logs:/app/logs -p 8501:8501 sentiment-monitor`
        Pre-populate logs with the evaluator, writing to the shared volume:
        `docker exec sentiment_api python /app/evaluate.py --api http://127.0.0.1:8000/predict --test /app/test_data.json`
        Verify it's up:
        `docker ps`
        You should see sentiment_api (PORTS 0.0.0.0:8000->8000/tcp) and sentiment_monitor (0.0.0.0:8501->8501/tcp). Get your instance’s Public IPv4 address from the EC2 console (should look something like 54.196.246.58), then open these links in the browser for further verification:
            - API docs: http://<PUBLIC_IP>:8000/docs
            - Dashboard: http://<PUBLIC_IP>:8501
        NOTE: it's not recommended to add another review in the dashboard. This is a tiny EC2 instance that can get easily overwhelmed.

6. Don't forget to close the instance! On the instances page, click the instance, click Instance state, and Stop instance. Then Stop in the bottom right. Then on the AWS Academy page, click End Lab (assuming you're working in the sandbox provided).

### Notes on using the dev branch

- First, make sure you're on your dev branch locally:
    `git checkout dev`

- Add updated files:
    `git add README.md`

- Commit them:
    `git commit -m "Update README"`

- Push to GitHub:
    `git push origin dev`

- To open a pull request, go to the GitHub repository, where you'll see a yellow banner: "dev had recent pushes less than a minute ago. Compare & pull request." If you don't see it, click the pull requests tab, click New pull request, and set base branch to main and compare branch to dev. Write a short title and description if you want. Submit the pull request by clicking Create pull request.

- To confirm CI/CD status: Once the PR is open, GitHub Actions will automatically trigger the workflow (ci.yml). You should see a status badge on the PR like All checks passed/Some checks failed/Check in progress.






### Full Assignment Text (#5, then #4) From MLOps Class

### Assignment 5 = CI/CD & Testing

This is the final and most comprehensive assignment. You will deploy your entire sentiment analysis system—the FastAPI backend and the Streamlit monitoring dashboard—onto a live cloud server (AWS EC2). You will also implement a professional CI/CD (Continuous Integration/Continuous Deployment) pipeline using GitHub Actions to automate testing and linting, ensuring code quality before deployment.

### System Architecture on EC2
- AWS EC2 Instance: A single virtual server running a Linux distribution (e.g., Ubuntu).

- Docker: You will install Docker on the EC2 instance to run your application.

- Services: The FastAPI backend and Streamlit dashboard will run as two separate Docker containers in detached mode (-d) on the same EC2 instance.


### Part 1: Preparing the Application for Production
In this part, you will enhance your existing project with tests to ensure reliability.

**Tasks:**

1. Create Test Files:

    - API Testing (api/test_api.py): Write tests for your FastAPI application using pytest. You must test:

        - The /predict endpoint with both a positive and a negative example.

        - That the endpoint correctly handles requests with missing or malformed data.

    - Dashboard Testing (monitoring/test_dashboard.py): Write at least one simple test for your Streamlit application to ensure it can launch without errors.


### Part 2: CI/CD with GitHub Actions
You will automate code quality checks for every pull request made to your main branch.

**Tasks:**

1. Set up Git Branches:

    - CREATE A NEW REPOSITORY FOR THIS ASSIGNMENT

    - All your work for this assignment must be done on a dev branch. The main branch should be protected.

2. Create the GitHub Actions Workflow:

    - In your repository, create the directory .github/workflows/.

    - Inside, create a YAML file (e.g., ci.yml). This workflow must:

        - **Trigger**: Be triggered automatically whenever a pull request is opened or updated against the mainbranch.

        - **Jobs**: Define a job that runs on an Ubuntu runner.

        - **Steps**: The job must perform the following steps in order:

            1. Check out the code from the repository.

            2. Set up a specific version of Python.

            3. Install all project dependencies fromrequirements.txt 

            4. **Linting**: Run a linter like flake8 or ruff against your Python code to check for style issues.

            5. **Testing**: Run your entire test suite using pytest.

 

### Part 3: Deployment to AWS EC2
This is the manual deployment process you will document.

**Tasks**:

1. Launch and Configure EC2 Instance:

    - Launch a new t2.micro EC2 instance with Ubuntu.

    - Configure its Security Group to allow incoming traffic on:

        - Port 22 (SSH) from your IP address for access.

        - Port 8000 (FastAPI) from anywhere.

        - Port 8501 (Streamlit) from anywhere.

    - Connect to your EC2 instance using SSH.

2. Set up the Server Environment:

    - On the EC2 instance, install Docker and Git.

3. Deploy the Application:

    - Clone your GitHub repository onto the EC2 instance.

    - Create a shared Docker volume for the logs.

    - Build the Docker images for both the api and monitoring services.

    - Run both containers in detached mode (-d), ensuring they are connected to the shared volume.

 

### Part 4: Documentation (The README.md)
Your README.md is the final, most critical piece. It must serve as a complete operational manual for your project.

**Tasks**:

- Update the README.md to include:

    1. Project Architecture: A clear description of the final architecture, including the FastAPI service, the Streamlit dashboard, the CI/CD pipeline, and the deployment on EC2.

    2. Local Development: Instructions on how to build and run the project locally using Docker.

    3. Manual Deployment Guide (Very Detailed): A step-by-step guide for a new developer to deploy this project from scratch. This must include:

        - How to launch and configure the EC2 instance and its security group.

        - All the commands needed to install dependencies (Git, Docker) on the server.

        - The exact docker commands to create the volume, build the images, and run the two containers in detached mode.

### Submission

- Create a pull request from your dev branch to your main branch on GitHub. The PR should show the status of your GitHub Actions checks. Do not merge it until after grading.

- Submit the URL to the pull request on your public GitHub repository. This will allow me (the instructor) to see both your code and the results of the automated CI/CD pipeline.

- Use the AWS sandbox for this assignment. I will not check your EC2 instance since it will not persist once you close it, instead I will replicate the steps you mentioned and clone it on my end to grade your work



----------------------------------------



### Assignment 4 - Model Monitoring

**Objective**: This assignment will introduce you to the MLOps practice of model monitoring. You will build a system that not only serves predictions but also actively monitors the model's performance and data integrity. You will create and run two distinct services—a FastAPI backend and a Streamlit dashboard—as separate Docker containers communicating over a shared network.

Note: This assignment is not based on Week 7 Labs

For this assignment, you need to have:

- A full understanding of the previous assignments covering FastAPI, Streamlit, and Docker.

- You will need the IMDB Dataset.csv and a trained sentiment_model.pkl file.


### System Architecture
You will build a multi-container application where two services run independently but communicate with each other:

1. FastAPI Prediction Service: A container running a FastAPI app that serves sentiment predictions and logs every request and response to a shared Docker volume.

2. Streamlit Monitoring Dashboard: A second container running a Streamlit app that reads the logs from the same shared volume to visualize model performance.

3. Docker Volume: A named volume to persist log data and share it between the two containers.

### The FastAPI Prediction Service:

This service should: 

- Build a simple FastAPI app with a prediction endpoint: POST /predict.

- For every request to /predict, your app must log a JSON object to a file named prediction_logs.jsonlocated in a /logs directory.

- Each log entry must be a new line in the JSON file and contain:

    - timestamp

    - request_text

    - predicted_sentiment

    - true_sentiment: This should be provided by the user through the feedback form (We won't have a frontend with a feedback form in this exercise). All requests will be mad through POSTMAN

### The Streamlit Monitoring Dashboard

(In a separate directory) This service should:

- Include a Streamlit app will that will read and parse the prediction_logs.json file from the shared /logs directory.

- The dashboard must display the following monitoring plots:

    - Data Drift Analysis: Create a histogram or density plot comparing the distribution of sentence lengths from your IMDB Dataset.csv against the lengths from the logged inference requests. 

    - Target Drift Analysis: Create a bar chart showing the distribution of predicted sentiments from the logs vs trained sentiments

    - Model Accuracy & User Feedback:

        - From the true_sentiment logged in the logs

        - Calculate and display the model's accuracy and precision based on all collected feedback.

        - Implement Alerting: If the calculated accuracy drops below 80%, display a prominent warning banner at the top of the dashboard using st.error().

### Evaluation Script

This part focuses on creating a script to systematically evaluate your API's performance.

**Create the Evaluation Script** (evaluate.py):

- Create this script in the root directory of your project.

- Use the test_data.json file: [{"text": "...", "true_label": "positive"}, ...]. (Provided at the end of this page)

- Your script must read the file, loop through each item, send the text to the running FastAPI service's /predict endpoint (e.g., at http://localhost:8000/predict), and print a final accuracy score.

- You may use the requests library from Python to do this.

### Packaging and Documentation

You will package the entire application using two separate Dockerfiles and a Makefile to orchestrate them.

1. Two Dockerfiles:

    - Create a api/Dockerfile for the FastAPI service.

    - Create a monitoring/Dockerfile for the Streamlit service.

2. Makefile: It must handle

    - build, run, and clean (to stop containers and remove the network/volume).

3. README.md: Your README must be updated to explain the new multi-container architecture and provide clear, step-by-step instructions on how to use the Makefile to run the entire stack. It must also include curl examples for the API and instructions for the evaluate.py script.

### Submission

Create a new public GitHub repository (Please do not use the ones created for previous assignments; else you will lose points)

 

Use this file to provide test inputs through your evaluate.py script (rather than having to type it all with POSTMAN) --> test.json