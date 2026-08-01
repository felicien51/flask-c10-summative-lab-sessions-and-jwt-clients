from config import app, api, db

from resources.auth import SignUp, Login, Logout, CheckSession
# from resources.tasks import TaskList, TaskDetail

api.add_resource(SignUp, "/signup")
api.add_resource(Login, "/login")
api.add_resource(Logout, "/logout")
api.add_resource(CheckSession, "/check_session")

# api.add_resource(TaskList, "/tasks")
# api.add_resource(TaskDetail, "/tasks/<int:id>")


@app.route("/")
def index():
    return {"message": "Productivity API is running"}


if __name__ == "__main__":
    app.run(port=5555, debug=True)