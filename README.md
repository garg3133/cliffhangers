# cliffhangers

## How to run it?

  * Download and install Python 3.7
  * Download and install Git.
  * Fork the Repository.
  * Clone the repository to your local machine `$ git clone https://github.com/<your-github-username>/NC_SVCE_MK199_CliffHangers.git`
  * Change directory to NC_SVCE_MK199_CliffHangers `$ cd NC_SVCE_MK199_CliffHangers`
  * Install virtualenv `$ pip3 install virtualenv`
  * Create a virtual environment `$ virtualenv env -p python3.7`  
  * Activate the env: `$ source env/bin/activate` (for linux) `> ./env/Scripts/activate` (for Windows PowerShell)
  * Install the requirements: `$ pip install -r requirements.txt`
  * Make migrations `$ python manage.py makemigrations`
  * Make migrations for 'accounts' app `$ python manage.py makemigrations accounts`
  * Make migrations for 'home' app `$ python manage.py makemigrations home`
  * Migrate the changes to the database `$ python manage.py migrate`
  * Create admin `$ python manage.py createsuperuser`
  * Run the server `$ python manage.py runserver`
