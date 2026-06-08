from todo_project.todo_project import app, db, models


def main():
    with app.app_context():
        db.create_all()

    app.run(host='0.0.0.0', port=5000, debug=False)


if __name__ == '__main__':
    main()