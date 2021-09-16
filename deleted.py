        # if request.form.get("register"):
        #     user = User(len(users), username, password)
        #     users.append(user)
        #     session["user_id"] = user.id
        # user = None

        # for user in users:
        #     if user.username == username and user.password == password:
        #         session['user_id'] = user.id
        #         return redirect(url_for("home"))
        #         #if the username and password is correct redirects to home




        
# class User:
#     def __init__(self, id, username, password):
#         self.id = id
#         self.username = username
#         self.password = password
    
#     def __repr__(self):
#         return f'<User: {self.username}>'
#         #shows the user's username instead of showing their id 

# users = []
# users.append(User(id=0, username = 'jasmine', password = 'hungry'))
# users.append(User(id=1, username = 'hanan', password = 'test'))
#adds intances of user classes