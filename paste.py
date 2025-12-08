members=[
    users(name="karthik", age=18,number="8121809638",salary=600000),
    users(name="raviteja", age=21,number="8885080235",salary=120000),
    users(name="harsha", age=19,number="8886888271",salary=120000)]
db = SessionLocal()
for member in members:
    exists = db.query(Users).filter(Users.name == member.name).first()
    if not exists:
        new_user = databasemodels.Users(
            name=member.name,
            age=member.age,
            number=member.number,
            salary=member.salary
        )
        db.add(new_user)
        db.commit()
db.close()