from connect_four import db, orm

session = db.get_session()
results = session.query(orm.NewUser).all()
for result in results:
    print(result.id, result.email, result.result)
